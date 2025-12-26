/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: cloud-ai-service.go                                                   ║
║  Generated: 2025-12-26T10:00:42.028789                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - CLOUD-AI-SERVICE.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/ollama/ollama/api"
	"github.com/redis/go-redis/v9"
	"github.com/joho/godotenv"
)

// CloudAIService represents the cloud AI service
type CloudAIService struct {
	OllamaClient *api.Client
	RedisClient  *redis.Client
	RateLimiter  *RateLimiter
	Cache        *AICache
	Config       *ServiceConfig
}

// ServiceConfig holds the service configuration
type ServiceConfig struct {
	Port           string
	RedisURL       string
	OllamaURL      string
	MaxRequests    int
	CacheTTL       time.Duration
	RateLimitWindow time.Duration
	APIKey         string
	Models         []string
}

// RateLimiter handles rate limiting
type RateLimiter struct {
	Redis    *redis.Client
	MaxReqs  int
	Window   time.Duration
}

// AICache handles response caching
type AICache struct {
	Redis *redis.Client
	TTL   time.Duration
}

// ChatRequest represents a chat completion request
type ChatRequest struct {
	Model       string    `json:"model" binding:"required"`
	Messages    []Message `json:"messages" binding:"required"`
	MaxTokens   int       `json:"max_tokens,omitempty"`
	Temperature float64   `json:"temperature,omitempty"`
	Stream      bool      `json:"stream,omitempty"`
}

// ChatResponse represents a chat completion response
type ChatResponse struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Created int64  `json:"created"`
	Model   string `json:"model"`
	Choices []struct {
		Index   int `json:"index"`
		Message struct {
			Role    string `json:"role"`
			Content string `json:"content"`
		} `json:"message"`
		FinishReason string `json:"finish_reason"`
	} `json:"choices"`
	Usage struct {
		PromptTokens     int `json:"prompt_tokens"`
		CompletionTokens int `json:"completion_tokens"`
		TotalTokens      int `json:"total_tokens"`
	} `json:"usage"`
}

// Message represents a chat message
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// ModelInfo represents model information
type ModelInfo struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Created int64  `json:"created"`
	OwnedBy string `json:"owned_by"`
}

// ModelsResponse represents the models list response
type ModelsResponse struct {
	Object string      `json:"object"`
	Data   []ModelInfo `json:"data"`
}

// HealthResponse represents health check response
type HealthResponse struct {
	Status    string            `json:"status"`
	Timestamp time.Time         `json:"timestamp"`
	Services  map[string]string `json:"services"`
	Stats     map[string]int    `json:"stats"`
}

// NewCloudAIService creates a new cloud AI service
func NewCloudAIService(config *ServiceConfig) (*CloudAIService, error) {
	// Initialize Ollama client
	ollamaClient := api.NewClient(config.OllamaURL)

	// Initialize Redis client
	redisClient := redis.NewClient(&redis.Options{
		Addr: config.RedisURL,
	})

	// Test Redis connection
	ctx := context.Background()
	if err := redisClient.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	// Initialize rate limiter
	rateLimiter := &RateLimiter{
		Redis:   redisClient,
		MaxReqs: config.MaxRequests,
		Window:  config.RateLimitWindow,
	}

	// Initialize cache
	cache := &AICache{
		Redis: redisClient,
		TTL:   config.CacheTTL,
	}

	return &CloudAIService{
		OllamaClient: ollamaClient,
		RedisClient:  redisClient,
		RateLimiter:  rateLimiter,
		Cache:        cache,
		Config:       config,
	}, nil
}

// Start starts the cloud AI service
func (s *CloudAIService) Start() error {
	// Set Gin mode
	gin.SetMode(gin.ReleaseMode)
	
	// Create router
	r := gin.Default()

	// Middleware
	r.Use(s.corsMiddleware())
	r.Use(s.authMiddleware())
	r.Use(s.rateLimitMiddleware())
	r.Use(s.loggingMiddleware())

	// Health check endpoint
	r.GET("/health", s.handleHealth)

	// API routes
	api := r.Group("/api/v1")
	{
		api.POST("/chat/completions", s.handleChatCompletion)
		api.GET("/models", s.handleListModels)
		api.POST("/code/analyze", s.handleCodeAnalysis)
		api.POST("/code/generate", s.handleCodeGeneration)
		api.POST("/github/analyze", s.handleGitHubAnalysis)
	}

	// Start server
	log.Printf("Starting Cloud AI Service on port %s", s.Config.Port)
	return r.Run(":" + s.Config.Port)
}

// handleHealth handles health check requests
func (s *CloudAIService) handleHealth(c *gin.Context) {
	// Check Ollama connection
	ollamaStatus := "healthy"
	if err := s.checkOllamaHealth(); err != nil {
		ollamaStatus = "unhealthy: " + err.Error()
	}

	// Check Redis connection
	redisStatus := "healthy"
	if err := s.RedisClient.Ping(context.Background()).Err(); err != nil {
		redisStatus = "unhealthy: " + err.Error()
	}

	// Get cache stats
	cacheStats := s.getCacheStats()

	response := HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now(),
		Services: map[string]string{
			"ollama": ollamaStatus,
			"redis":  redisStatus,
		},
		Stats: cacheStats,
	}

	// Set overall status
	if ollamaStatus != "healthy" || redisStatus != "healthy" {
		response.Status = "degraded"
	}

	c.JSON(http.StatusOK, response)
}

// handleChatCompletion handles chat completion requests
func (s *CloudAIService) handleChatCompletion(c *gin.Context) {
	var req ChatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set defaults
	if req.MaxTokens == 0 {
		req.MaxTokens = 1000
	}
	if req.Temperature == 0 {
		req.Temperature = 0.7
	}

	// Check cache first
	cacheKey := s.generateCacheKey(req)
	if cached, exists := s.Cache.Get(cacheKey); exists {
		c.JSON(http.StatusOK, cached)
		return
	}

	// Generate response using Ollama
	response, err := s.generateResponse(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Cache response
	s.Cache.Set(cacheKey, response)

	c.JSON(http.StatusOK, response)
}

// handleListModels handles model listing requests
func (s *CloudAIService) handleListModels(c *gin.Context) {
	// Get available models from Ollama
	models, err := s.OllamaClient.List(context.Background())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Convert to API format
	var modelList []ModelInfo
	for _, model := range models.Models {
		modelList = append(modelList, ModelInfo{
			ID:      model.Name,
			Object:  "model",
			Created: time.Now().Unix(),
			OwnedBy: "go-ai-coder",
		})
	}

	response := ModelsResponse{
		Object: "list",
		Data:   modelList,
	}

	c.JSON(http.StatusOK, response)
}

// handleCodeAnalysis handles code analysis requests
func (s *CloudAIService) handleCodeAnalysis(c *gin.Context) {
	var req struct {
		Code  string `json:"code" binding:"required"`
		Model string `json:"model,omitempty"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.Model == "" {
		req.Model = "codellama:13b"
	}

	// Create analysis prompt
	prompt := fmt.Sprintf("Analyze this Go code and provide insights:\n\n```go\n%s\n```\n\nProvide:\n1. Code quality assessment\n2. Potential improvements\n3. Best practices suggestions\n4. Performance considerations", req.Code)

	// Generate analysis
	chatReq := ChatRequest{
		Model: req.Model,
		Messages: []Message{
			{Role: "system", Content: "You are an expert Go developer. Provide detailed, actionable code analysis."},
			{Role: "user", Content: prompt},
		},
		MaxTokens:   2000,
		Temperature: 0.3,
	}

	response, err := s.generateResponse(chatReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// handleCodeGeneration handles code generation requests
func (s *CloudAIService) handleCodeGeneration(c *gin.Context) {
	var req struct {
		Prompt string `json:"prompt" binding:"required"`
		Model  string `json:"model,omitempty"`
		Type   string `json:"type,omitempty"` // function, struct, test, etc.
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.Model == "" {
		req.Model = "codellama:13b"
	}

	// Create generation prompt
	systemPrompt := "You are an expert Go developer. Generate clean, idiomatic Go code that follows best practices."
	userPrompt := fmt.Sprintf("Generate Go %s code for: %s", req.Type, req.Prompt)

	chatReq := ChatRequest{
		Model: req.Model,
		Messages: []Message{
			{Role: "system", Content: systemPrompt},
			{Role: "user", Content: userPrompt},
		},
		MaxTokens:   2000,
		Temperature: 0.5,
	}

	response, err := s.generateResponse(chatReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// handleGitHubAnalysis handles GitHub repository analysis requests
func (s *CloudAIService) handleGitHubAnalysis(c *gin.Context) {
	var req struct {
		Repository string `json:"repository" binding:"required"`
		Analysis   string `json:"analysis,omitempty"` // code, issues, prs, etc.
		Model      string `json:"model,omitempty"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.Model == "" {
		req.Model = "llama3.2:3b"
	}

	// Create analysis prompt
	prompt := fmt.Sprintf("Analyze the GitHub repository '%s' and provide insights about %s. Focus on Go-specific aspects if applicable.", req.Repository, req.Analysis)

	chatReq := ChatRequest{
		Model: req.Model,
		Messages: []Message{
			{Role: "system", Content: "You are an expert software engineer. Provide detailed repository analysis."},
			{Role: "user", Content: prompt},
		},
		MaxTokens:   2000,
		Temperature: 0.4,
	}

	response, err := s.generateResponse(chatReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// generateResponse generates a response using Ollama
func (s *CloudAIService) generateResponse(req ChatRequest) (*ChatResponse, error) {
	// Convert messages to Ollama format
	var messages []api.Message
	for _, msg := range req.Messages {
		messages = append(messages, api.Message{
			Role:    msg.Role,
			Content: msg.Content,
		})
	}

	// Create Ollama request
	ollamaReq := &api.ChatRequest{
		Model:    req.Model,
		Messages: messages,
		Options: api.Options{
			Temperature: req.Temperature,
			NumPredict:  req.MaxTokens,
		},
		Stream: &req.Stream,
	}

	// Send request to Ollama
	ctx := context.Background()
	resp, err := s.OllamaClient.Chat(ctx, ollamaReq)
	if err != nil {
		return nil, fmt.Errorf("failed to generate response: %w", err)
	}

	// Convert to API response format
	response := &ChatResponse{
		ID:      fmt.Sprintf("chatcmpl-%d", time.Now().Unix()),
		Object:  "chat.completion",
		Created: time.Now().Unix(),
		Model:   req.Model,
		Choices: []struct {
			Index   int `json:"index"`
			Message struct {
				Role    string `json:"role"`
				Content string `json:"content"`
			} `json:"message"`
			FinishReason string `json:"finish_reason"`
		}{
			{
				Index: 0,
				Message: struct {
					Role    string `json:"role"`
					Content string `json:"content"`
				}{
					Role:    "assistant",
					Content: resp.Message.Content,
				},
				FinishReason: "stop",
			},
		},
		Usage: struct {
			PromptTokens     int `json:"prompt_tokens"`
			CompletionTokens int `json:"completion_tokens"`
			TotalTokens      int `json:"total_tokens"`
		}{
			PromptTokens:     len(req.Messages) * 100, // Estimate
			CompletionTokens: len(resp.Message.Content) / 4, // Estimate
			TotalTokens:      len(req.Messages)*100 + len(resp.Message.Content)/4,
		},
	}

	return response, nil
}

// generateCacheKey generates a cache key for a request
func (s *CloudAIService) generateCacheKey(req ChatRequest) string {
	// Create a hash of the request for caching
	data, _ := json.Marshal(req)
	return fmt.Sprintf("chat:%x", data)
}

// checkOllamaHealth checks if Ollama is healthy
func (s *CloudAIService) checkOllamaHealth() error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	_, err := s.OllamaClient.List(ctx)
	return err
}

// getCacheStats returns cache statistics
func (s *CloudAIService) getCacheStats() map[string]int {
	ctx := context.Background()
	
	// Get Redis info
	info, err := s.RedisClient.Info(ctx, "memory").Result()
	if err != nil {
		return map[string]int{"error": 1}
	}

	// Parse memory usage (simplified)
	stats := map[string]int{
		"cache_entries": 0, // Would need to count keys
		"memory_usage":  0, // Would parse from info
	}

	return stats
}

// Middleware functions
func (s *CloudAIService) corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	}
}

func (s *CloudAIService) authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Skip auth for health check
		if c.Request.URL.Path == "/health" {
			c.Next()
			return
		}

		// Check API key
		apiKey := c.GetHeader("Authorization")
		if apiKey == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "API key required"})
			c.Abort()
			return
		}

		// Validate API key (simplified)
		if apiKey != "Bearer "+s.Config.APIKey {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid API key"})
			c.Abort()
			return
		}

		c.Next()
	}
}

func (s *CloudAIService) rateLimitMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		clientIP := c.ClientIP()
		
		if !s.RateLimiter.Allow(clientIP) {
			c.JSON(http.StatusTooManyRequests, gin.H{"error": "Rate limit exceeded"})
			c.Abort()
			return
		}
		
		c.Next()
	}
}

func (s *CloudAIService) loggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		
		log.Printf("%s %s %d %v",
			c.Request.Method,
			c.Request.URL.Path,
			c.Writer.Status(),
			time.Since(start),
		)
	}
}

// RateLimiter methods
func (r *RateLimiter) Allow(clientIP string) bool {
	ctx := context.Background()
	key := fmt.Sprintf("rate_limit:%s", clientIP)
	
	// Get current count
	count, err := r.Redis.Get(ctx, key).Int()
	if err != nil && err != redis.Nil {
		return true // Allow on error
	}
	
	// Check if over limit
	if count >= r.MaxReqs {
		return false
	}
	
	// Increment counter
	pipe := r.Redis.Pipeline()
	pipe.Incr(ctx, key)
	pipe.Expire(ctx, key, r.Window)
	_, err = pipe.Exec(ctx)
	
	return err == nil
}

// AICache methods
func (c *AICache) Get(key string) (interface{}, bool) {
	ctx := context.Background()
	val, err := c.Redis.Get(ctx, key).Result()
	if err != nil {
		return nil, false
	}
	
	var result interface{}
	if err := json.Unmarshal([]byte(val), &result); err != nil {
		return nil, false
	}
	
	return result, true
}

func (c *AICache) Set(key string, value interface{}) {
	ctx := context.Background()
	data, err := json.Marshal(value)
	if err != nil {
		return
	}
	
	c.Redis.Set(ctx, key, data, c.TTL)
}

// Load configuration from environment
func loadServiceConfig() *ServiceConfig {
	godotenv.Load()
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	
	maxReqs, _ := strconv.Atoi(os.Getenv("MAX_REQUESTS"))
	if maxReqs == 0 {
		maxReqs = 100
	}
	
	cacheTTL, _ := time.ParseDuration(os.Getenv("CACHE_TTL"))
	if cacheTTL == 0 {
		cacheTTL = 5 * time.Minute
	}
	
	rateLimitWindow, _ := time.ParseDuration(os.Getenv("RATE_LIMIT_WINDOW"))
	if rateLimitWindow == 0 {
		rateLimitWindow = time.Minute
	}
	
	return &ServiceConfig{
		Port:            port,
		RedisURL:        getEnv("REDIS_URL", "localhost:6379"),
		OllamaURL:       getEnv("OLLAMA_URL", "http://localhost:11434"),
		MaxRequests:     maxReqs,
		CacheTTL:        cacheTTL,
		RateLimitWindow: rateLimitWindow,
		APIKey:          getEnv("API_KEY", "your-secret-api-key"),
		Models:          []string{"llama3.2:3b", "codellama:13b", "deepseek-coder:6.7b"},
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// Main function
func main() {
	// Load configuration
	config := loadServiceConfig()
	
	// Create service
	service, err := NewCloudAIService(config)
	if err != nil {
		log.Fatalf("Failed to create service: %v", err)
	}
	
	// Start service
	if err := service.Start(); err != nil {
		log.Fatalf("Failed to start service: %v", err)
	}
}
