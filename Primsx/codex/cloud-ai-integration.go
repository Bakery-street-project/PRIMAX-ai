/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: cloud-ai-integration.go                                               ║
║  Generated: 2025-12-26T10:00:42.027526                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - CLOUD-AI-INTEGRATION.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

// CloudAIClient represents a hybrid AI client that can use both cloud and local AI
type CloudAIClient struct {
	CloudURL      string
	LocalURL      string
	APIKey        string
	FallbackMode  bool
	Cache         *AICache
	RateLimiter   *RateLimiter
	LastUsed      time.Time
	CloudAvailable bool
}

// AICache handles caching of AI responses
type AICache struct {
	Responses map[string]CachedResponse
	MaxSize   int
	TTL       time.Duration
}

// CachedResponse represents a cached AI response
type CachedResponse struct {
	Response   string
	Timestamp  time.Time
	Model      string
	Tokens     int
}

// RateLimiter handles rate limiting for API calls
type RateLimiter struct {
	Requests    map[string][]time.Time
	MaxRequests int
	Window      time.Duration
}

// CloudAIRequest represents a request to the cloud AI service
type CloudAIRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	MaxTokens   int       `json:"max_tokens"`
	Temperature float64   `json:"temperature"`
	Stream      bool      `json:"stream"`
}

// CloudAIResponse represents a response from the cloud AI service
type CloudAIResponse struct {
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

// NewCloudAIClient creates a new hybrid AI client
func NewCloudAIClient(cloudURL, localURL, apiKey string, fallbackMode bool) *CloudAIClient {
	return &CloudAIClient{
		CloudURL:      cloudURL,
		LocalURL:      localURL,
		APIKey:        apiKey,
		FallbackMode:  fallbackMode,
		Cache:         NewAICache(1000, 5*time.Minute),
		RateLimiter:   NewRateLimiter(100, time.Minute),
		CloudAvailable: true,
	}
}

// NewAICache creates a new AI cache
func NewAICache(maxSize int, ttl time.Duration) *AICache {
	return &AICache{
		Responses: make(map[string]CachedResponse),
		MaxSize:   maxSize,
		TTL:       ttl,
	}
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(maxRequests int, window time.Duration) *RateLimiter {
	return &RateLimiter{
		Requests:    make(map[string][]time.Time),
		MaxRequests: maxRequests,
		Window:      window,
	}
}

// SendMessage sends a message to the AI service with smart fallback
func (c *CloudAIClient) SendMessage(message string, model string, maxTokens int, temperature float64) (string, error) {
	// Check cache first
	cacheKey := fmt.Sprintf("%s:%s:%d:%.2f", message, model, maxTokens, temperature)
	if cached, exists := c.Cache.Get(cacheKey); exists {
		fmt.Println("[CACHE] Using cached response")
		return cached, nil
	}

	// Try cloud AI first
	if c.CloudAvailable && c.CloudURL != "" {
		response, err := c.sendToCloud(message, model, maxTokens, temperature)
		if err == nil {
			c.Cache.Set(cacheKey, response)
			c.LastUsed = time.Now()
			return response, nil
		}
		
		// Mark cloud as unavailable temporarily
		c.CloudAvailable = false
		fmt.Printf("[WARNING] Cloud AI unavailable: %v\n", err)
	}

	// Fallback to local AI
	if c.FallbackMode && c.LocalURL != "" {
		response, err := c.sendToLocal(message, model, maxTokens, temperature)
		if err == nil {
			c.Cache.Set(cacheKey, response)
			c.LastUsed = time.Now()
			return response, nil
		}
		return "", fmt.Errorf("local AI also failed: %w", err)
	}

	return "", fmt.Errorf("both cloud and local AI unavailable")
}

// sendToCloud sends a request to the cloud AI service
func (c *CloudAIClient) sendToCloud(message string, model string, maxTokens int, temperature float64) (string, error) {
	// Check rate limiting
	if !c.RateLimiter.Allow("cloud") {
		return "", fmt.Errorf("rate limit exceeded for cloud AI")
	}

	// Prepare request
	req := CloudAIRequest{
		Model: model,
		Messages: []Message{
			{Role: "system", Content: "You are a helpful AI coding assistant specialized in Go programming. Provide concise, accurate, and helpful responses."},
			{Role: "user", Content: message},
		},
		MaxTokens:   maxTokens,
		Temperature: temperature,
		Stream:      false,
	}

	// Marshal request
	reqBody, err := json.Marshal(req)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %w", err)
	}

	// Create HTTP request
	httpReq, err := http.NewRequest("POST", c.CloudURL+"/api/v1/chat/completions", bytes.NewBuffer(reqBody))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+c.APIKey)
	httpReq.Header.Set("User-Agent", "go-ai-coder/1.0")

	// Send request
	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(httpReq)
	if err != nil {
		return "", fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	// Check status code
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("cloud AI returned status %d: %s", resp.StatusCode, string(body))
	}

	// Parse response
	var aiResp CloudAIResponse
	if err := json.NewDecoder(resp.Body).Decode(&aiResp); err != nil {
		return "", fmt.Errorf("failed to decode response: %w", err)
	}

	if len(aiResp.Choices) == 0 {
		return "", fmt.Errorf("no response choices received")
	}

	return aiResp.Choices[0].Message.Content, nil
}

// sendToLocal sends a request to the local Ollama service
func (c *CloudAIClient) sendToLocal(message string, model string, maxTokens int, temperature float64) (string, error) {
	// Check rate limiting
	if !c.RateLimiter.Allow("local") {
		return "", fmt.Errorf("rate limit exceeded for local AI")
	}

	// Create OpenAI client for local Ollama
	client := openai.NewClient(
		option.WithAPIKey("ollama"),
		option.WithBaseURL(c.LocalURL),
	)

	// Prepare messages
	messages := []openai.ChatCompletionMessageParamUnion{
		openai.SystemMessage("You are a helpful AI coding assistant specialized in Go programming. Provide concise, accurate, and helpful responses."),
		openai.UserMessage(message),
	}

	// Create completion request
	req := openai.ChatCompletionNewParams{
		Model:       model,
		Messages:    messages,
		MaxTokens:   openai.Int(int64(maxTokens)),
		Temperature: openai.Float(temperature),
		TopP:        openai.Float(0.9),
	}

	// Send request
	ctx := context.Background()
	resp, err := client.Chat.Completions.New(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to create chat completion: %w", err)
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response choices received")
	}

	return resp.Choices[0].Message.Content, nil
}

// Get retrieves a cached response
func (c *AICache) Get(key string) (string, bool) {
	cached, exists := c.Responses[key]
	if !exists {
		return "", false
	}

	// Check if expired
	if time.Since(cached.Timestamp) > c.TTL {
		delete(c.Responses, key)
		return "", false
	}

	return cached.Response, true
}

// Set stores a response in cache
func (c *AICache) Set(key string, response string) {
	// Check cache size
	if len(c.Responses) >= c.MaxSize {
		// Remove oldest entry
		var oldestKey string
		var oldestTime time.Time
		for k, v := range c.Responses {
			if oldestTime.IsZero() || v.Timestamp.Before(oldestTime) {
				oldestTime = v.Timestamp
				oldestKey = k
			}
		}
		delete(c.Responses, oldestKey)
	}

	// Store new response
	c.Responses[key] = CachedResponse{
		Response:  response,
		Timestamp: time.Now(),
	}
}

// Allow checks if a request is allowed based on rate limiting
func (r *RateLimiter) Allow(service string) bool {
	now := time.Now()
	
	// Clean old requests
	if requests, exists := r.Requests[service]; exists {
		var validRequests []time.Time
		for _, reqTime := range requests {
			if now.Sub(reqTime) < r.Window {
				validRequests = append(validRequests, reqTime)
			}
		}
		r.Requests[service] = validRequests
	}

	// Check if under limit
	if len(r.Requests[service]) >= r.MaxRequests {
		return false
	}

	// Add current request
	r.Requests[service] = append(r.Requests[service], now)
	return true
}

// HealthCheck checks the health of both cloud and local AI services
func (c *CloudAIClient) HealthCheck() map[string]bool {
	health := make(map[string]bool)

	// Check cloud AI
	if c.CloudURL != "" {
		client := &http.Client{Timeout: 5 * time.Second}
		resp, err := client.Get(c.CloudURL + "/health")
		health["cloud"] = err == nil && resp.StatusCode == http.StatusOK
		if resp != nil {
			resp.Body.Close()
		}
	} else {
		health["cloud"] = false
	}

	// Check local AI
	if c.LocalURL != "" {
		client := &http.Client{Timeout: 5 * time.Second}
		resp, err := client.Get(c.LocalURL + "/api/tags")
		health["local"] = err == nil && resp.StatusCode == http.StatusOK
		if resp != nil {
			resp.Body.Close()
		}
	} else {
		health["local"] = false
	}

	return health
}

// GetStats returns statistics about the AI client
func (c *CloudAIClient) GetStats() map[string]interface{} {
	stats := make(map[string]interface{})
	
	stats["cache_size"] = len(c.Cache.Responses)
	stats["cache_max_size"] = c.Cache.MaxSize
	stats["last_used"] = c.LastUsed
	stats["cloud_available"] = c.CloudAvailable
	stats["fallback_mode"] = c.FallbackMode
	
	// Rate limiter stats
	stats["rate_limits"] = make(map[string]int)
	for service, requests := range c.RateLimiter.Requests {
		stats["rate_limits"].(map[string]int)[service] = len(requests)
	}
	
	return stats
}
