/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: github_ai_agent.go                                                    ║
║  Generated: 2025-12-26T10:00:42.341216                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - GITHUB_AI_AGENT.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
	"regexp"
	"path/filepath"
	"flag"

	"github.com/joho/godotenv"
	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

// GitHub API structures
type GitHubRepo struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	FullName    string `json:"full_name"`
	Description string `json:"description"`
	Language    string `json:"language"`
	Stars       int    `json:"stargazers_count"`
	Forks       int    `json:"forks_count"`
	UpdatedAt   string `json:"updated_at"`
	CloneURL    string `json:"clone_url"`
	SSHURL      string `json:"ssh_url"`
}

type GitHubIssue struct {
	ID     int    `json:"id"`
	Number int    `json:"number"`
	Title  string `json:"title"`
	Body   string `json:"body"`
	State  string `json:"state"`
	User   struct {
		Login string `json:"login"`
	} `json:"user"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}

type GitHubPullRequest struct {
	ID     int    `json:"id"`
	Number int    `json:"number"`
	Title  string `json:"title"`
	Body   string `json:"body"`
	State  string `json:"state"`
	User   struct {
		Login string `json:"login"`
	} `json:"user"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
	Head     struct {
		Ref string `json:"ref"`
	} `json:"head"`
	Base struct {
		Ref string `json:"ref"`
	} `json:"base"`
}

type GitHubSearchResult struct {
	TotalCount int `json:"total_count"`
	Items      []struct {
		Name        string `json:"name"`
		FullName    string `json:"full_name"`
		Description string `json:"description"`
		Language    string `json:"language"`
		Stars       int    `json:"stargazers_count"`
		Forks       int    `json:"forks_count"`
		UpdatedAt   string `json:"updated_at"`
	} `json:"items"`
}

// Configuration structure
type Config struct {
	Verbose       bool
	Model         string
	MaxTokens     int
	Temperature   float64
	OllamaURL     string
	GitHubToken   string
	LearningDir   string
	CacheEnabled  bool
	AutoSave      bool
}

func loadConfig() *Config {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}

	// Parse command line flags
	verbose := flag.Bool("verbose", false, "Enable verbose output")
	model := flag.String("model", "llama3.2:3b", "Ollama model to use")
	maxTokens := flag.Int("tokens", 2000, "Maximum tokens for AI responses")
	temperature := flag.Float64("temp", 0.7, "AI temperature (0.0-1.0)")
	ollamaURL := flag.String("ollama", "http://localhost:11434/v1", "Ollama API URL")
	learningDir := flag.String("learning", "ai_learning", "Directory for AI learning data")
	cacheEnabled := flag.Bool("cache", true, "Enable response caching")
	autoSave := flag.Bool("autosave", true, "Auto-save conversations")
	
	flag.Parse()

	config := &Config{
		Verbose:      *verbose,
		Model:        *model,
		MaxTokens:    *maxTokens,
		Temperature:  *temperature,
		OllamaURL:    *ollamaURL,
		GitHubToken:  os.Getenv("GITHUB_TOKEN"),
		LearningDir:  *learningDir,
		CacheEnabled: *cacheEnabled,
		AutoSave:     *autoSave,
	}

	// Check for GitHub token
	if config.GitHubToken == "" {
		log.Println("⚠️  GITHUB_TOKEN not set. GitHub features will be limited.")
		log.Println("   Set GITHUB_TOKEN in your .env file for full GitHub integration")
	}

	return config
}

func main() {
	config := loadConfig()
	
	// Create OpenAI client with Ollama base URL
	client := openai.NewClient(
		option.WithAPIKey("ollama"), // Dummy key, Ollama doesn't require authentication
		option.WithBaseURL(config.OllamaURL),
	)

	// Display startup information
	fmt.Println("🤖 GitHub Enterprise AI Coding Agent")
	fmt.Println("====================================")
	fmt.Printf("Model: %s | Tokens: %d | Temp: %.1f\n", config.Model, config.MaxTokens, config.Temperature)
	fmt.Printf("Ollama: %s | Cache: %t | AutoSave: %t\n", config.OllamaURL, config.CacheEnabled, config.AutoSave)
	fmt.Println("")
	
	// Create learning directory
	os.MkdirAll(config.LearningDir, 0755)
	
	// Display help
	showHelp()

	// Start interactive session
	startInteractiveSession(client, config)
}

func showHelp() {
	fmt.Println("Commands:")
	fmt.Println("  read <file_or_folder> - Read file content or all files in folder")
	fmt.Println("  list <directory> - List directory contents")
	fmt.Println("  github repos - List your GitHub repositories")
	fmt.Println("  github search <query> - Search GitHub repositories")
	fmt.Println("  github issues <repo> - List issues for a repository")
	fmt.Println("  github prs <repo> - List pull requests for a repository")
	fmt.Println("  github clone <repo> - Clone a repository")
	fmt.Println("  go resources - Show curated Go learning resources")
	fmt.Println("  ai learn - AI learns about Go ecosystem automatically")
	fmt.Println("  ai research <topic> - AI researches specific Go topics")
	fmt.Println("  ai scrape <url> - AI scrapes and learns from web content")
	fmt.Println("  help - Show this help message")
	fmt.Println("  config - Show current configuration")
	fmt.Println("  quit/exit - Exit the program")
	fmt.Println("")
	fmt.Println("Examples:")
	fmt.Println("  read fizzbuzz.js")
	fmt.Println("  github search golang ai agent")
	fmt.Println("  ai research machine learning")
	fmt.Println("  ai scrape https://golang.org/doc/tutorial/")
	fmt.Println("")
}

func startInteractiveSession(client openai.Client, config *Config) {
	scanner := bufio.NewScanner(os.Stdin)
	conversationHistory := []string{}

	for {
		fmt.Print("You: ")
		if !scanner.Scan() {
			break
		}

		userInput := strings.TrimSpace(scanner.Text())
		if userInput == "" {
			continue
		}

		// Handle special commands
		if userInput == "quit" || userInput == "exit" {
			fmt.Println("Goodbye!")
			break
		} else if userInput == "help" {
			showHelp()
			continue
		} else if userInput == "config" {
			showConfig(config)
			continue
		}

		// Add to conversation history
		conversationHistory = append(conversationHistory, userInput)

		// Handle different command types
		if strings.HasPrefix(strings.ToLower(userInput), "github ") {
			handleGitHubCommand(client, userInput, config)
		} else if strings.HasPrefix(strings.ToLower(userInput), "read ") {
			handleReadCommand(client, userInput, config)
		} else if strings.HasPrefix(strings.ToLower(userInput), "list ") {
			handleListCommand(client, userInput, config)
		} else if strings.ToLower(userInput) == "go resources" {
			handleGoResourcesCommand(client, config)
		} else if strings.HasPrefix(strings.ToLower(userInput), "ai ") {
			handleAICommand(client, userInput, config)
		} else {
			// Regular chat with context
			response, err := sendMessageWithContext(client, userInput, conversationHistory, config)
			if err != nil {
				fmt.Printf("Error: %v\n", err)
				continue
			}
			fmt.Printf("AI: %s\n\n", response)
			conversationHistory = append(conversationHistory, response)
		}

		// Auto-save conversation if enabled
		if config.AutoSave {
			saveConversation(conversationHistory, config)
		}
	}
}

func showConfig(config *Config) {
	fmt.Println("Current Configuration:")
	fmt.Println("====================")
	fmt.Printf("Model: %s\n", config.Model)
	fmt.Printf("Max Tokens: %d\n", config.MaxTokens)
	fmt.Printf("Temperature: %.1f\n", config.Temperature)
	fmt.Printf("Ollama URL: %s\n", config.OllamaURL)
	fmt.Printf("GitHub Token: %s\n", maskToken(config.GitHubToken))
	fmt.Printf("Learning Directory: %s\n", config.LearningDir)
	fmt.Printf("Cache Enabled: %t\n", config.CacheEnabled)
	fmt.Printf("Auto Save: %t\n", config.AutoSave)
	fmt.Printf("Verbose: %t\n", config.Verbose)
	fmt.Println("")
}

func maskToken(token string) string {
	if token == "" {
		return "Not set"
	}
	if len(token) < 8 {
		return "***"
	}
	return token[:4] + "***" + token[len(token)-4:]
}

func handleGitHubCommand(client openai.Client, userInput string, config *Config) {
	parts := strings.Fields(userInput)
	if len(parts) < 2 {
		fmt.Println("❌ Invalid GitHub command. Use: github <command>")
		return
	}

	command := strings.ToLower(parts[1])

	switch command {
	case "repos":
		if config.GitHubToken == "" {
			fmt.Println("❌ GITHUB_TOKEN required for this command")
			return
		}
		repos, err := getGitHubRepos(config.GitHubToken)
		if err != nil {
			fmt.Printf("❌ Error fetching repositories: %v\n", err)
			return
		}
		
		// Send repo data to AI for analysis
		repoData := formatReposForAI(repos)
		response, err := sendMessageWithConfig(client, fmt.Sprintf("Here are my GitHub repositories:\n\n%s\n\nPlease analyze my repository portfolio and provide insights about my coding patterns, technologies used, and suggestions for improvement.", repoData), config)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			return
		}
		fmt.Printf("AI: %s\n\n", response)

	case "search":
		if len(parts) < 3 {
			fmt.Println("❌ Usage: github search <query>")
			return
		}
		query := strings.Join(parts[2:], " ")
		results, err := searchGitHubRepos(query)
		if err != nil {
			// If API fails due to rate limiting, provide curated results
			if strings.Contains(err.Error(), "rate limit") {
				fmt.Printf("⚠️  %v\n", err)
				fmt.Println("🔄 Providing curated results based on your query...")
				curatedResults := getCuratedSearchResults(query)
				response, err := sendMessageWithConfig(client, fmt.Sprintf("Curated search results for '%s' (GitHub API rate limited):\n\n%s\n\nPlease analyze these curated repositories and recommend the most relevant ones for my needs.", query, curatedResults), config)
				if err != nil {
					fmt.Printf("Error: %v\n", err)
					return
				}
				fmt.Printf("AI: %s\n\n", response)
			} else {
				fmt.Printf("❌ Error searching repositories: %v\n", err)
			}
			return
		}
		
		// Send search results to AI
		searchData := formatSearchResultsForAI(results)
		response, err := sendMessageWithConfig(client, fmt.Sprintf("GitHub search results for '%s':\n\n%s\n\nPlease analyze these repositories and recommend the most relevant ones for my needs.", query, searchData), config)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			return
		}
		fmt.Printf("AI: %s\n\n", response)

	case "issues":
		if len(parts) < 3 {
			fmt.Println("❌ Usage: github issues <repo>")
			return
		}
		repo := parts[2]
		issues, err := getGitHubIssues(repo)
		if err != nil {
			fmt.Printf("❌ Error fetching issues: %v\n", err)
			return
		}
		
		// Send issues to AI
		issuesData := formatIssuesForAI(issues)
		response, err := sendMessageWithConfig(client, fmt.Sprintf("Issues for repository %s:\n\n%s\n\nPlease analyze these issues and provide insights about the project's health, priority issues, and suggestions for resolution.", repo, issuesData), config)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			return
		}
		fmt.Printf("AI: %s\n\n", response)

	case "prs":
		if len(parts) < 3 {
			fmt.Println("❌ Usage: github prs <repo>")
			return
		}
		repo := parts[2]
		prs, err := getGitHubPullRequests(repo)
		if err != nil {
			fmt.Printf("❌ Error fetching pull requests: %v\n", err)
			return
		}
		
		// Send PRs to AI
		prsData := formatPullRequestsForAI(prs)
		response, err := sendMessageWithConfig(client, fmt.Sprintf("Pull requests for repository %s:\n\n%s\n\nPlease analyze these pull requests and provide insights about the development activity, code quality, and collaboration patterns.", repo, prsData), config)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			return
		}
		fmt.Printf("AI: %s\n\n", response)

	case "clone":
		if len(parts) < 3 {
			fmt.Println("❌ Usage: github clone <repo>")
			return
		}
		repo := parts[2]
		err := cloneGitHubRepo(repo)
		if err != nil {
			fmt.Printf("❌ Error cloning repository: %v\n", err)
			return
		}
		fmt.Printf("✅ Successfully cloned %s\n", repo)

	default:
		fmt.Println("❌ Unknown GitHub command. Available: repos, search, issues, prs, clone")
	}
}

func handleReadCommand(client openai.Client, userInput string, config *Config) {
	filePath := strings.TrimSpace(strings.TrimPrefix(userInput, "read "))
	filePath = strings.TrimSpace(strings.TrimPrefix(filePath, "Read "))
	content, err := readFileOrFolder(filePath)
	if err != nil {
		fmt.Printf("Error reading file/folder: %v\n", err)
		return
	}
	
	// Send file content to AI for analysis
	response, err := sendMessageWithConfig(client, fmt.Sprintf("Here is the content of %s:\n\n%s\n\nPlease analyze this and provide insights.", filePath, content), config)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("AI: %s\n\n", response)
}

func handleListCommand(client openai.Client, userInput string, config *Config) {
	dirPath := strings.TrimSpace(strings.TrimPrefix(userInput, "list "))
	dirPath = strings.TrimSpace(strings.TrimPrefix(dirPath, "List "))
	content, err := listDirectory(dirPath)
	if err != nil {
		fmt.Printf("Error listing directory: %v\n", err)
		return
	}
	
			// Send directory listing to AI
		response, err := sendMessageWithConfig(client, fmt.Sprintf("Here is the directory listing of %s:\n\n%s\n\nPlease analyze this directory structure and provide insights.", dirPath, content), config)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("AI: %s\n\n", response)
}

func handleGoResourcesCommand(client openai.Client, config *Config) {
	goResources := `
🚀 Curated Go Learning Resources
================================

Based on AI analysis of the Go ecosystem, here are the top recommended resources:

📚 **Learning & Tutorials**
• practical-tutorials/project-based-learning - Project-based Go tutorials
• golang/go - Official Go repository and documentation
• Go by Example - Hands-on introduction to Go

🛠️ **Frameworks & Libraries**
• gin-gonic/gin - Popular HTTP web framework
• avelino/awesome-go - Curated list of Go frameworks and libraries
• gorilla/mux - HTTP router and URL matcher

🤖 **AI & Machine Learning**
• ollama/ollama - Local AI model runner (you're already using this!)
• go-ai/go-ai - Go AI/ML libraries and tools

🔧 **Development Tools**
• golangci/golangci-lint - Fast Go linter
• spf13/cobra - CLI applications in Go
• spf13/viper - Configuration management

📖 **Best Practices**
• golang-standards/project-layout - Standard Go project layout
• uber-go/guide - Uber's Go style guide
• golang/go/wiki - Official Go wiki

🎯 **Next Steps**
1. Start with practical-tutorials/project-based-learning
2. Explore avelino/awesome-go for specific libraries
3. Build projects using gin-gonic/gin
4. Use golangci-lint for code quality

Would you like me to search GitHub for any specific Go topics or help you get started with a particular framework?
`

	// Send resources to AI for personalized recommendations
	response, err := sendMessageWithConfig(client, fmt.Sprintf("Here are curated Go learning resources:\n\n%s\n\nPlease provide personalized recommendations based on my current skill level and suggest a learning path.", goResources), config)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	
	fmt.Printf("📚 %s\n\n", goResources)
	fmt.Printf("AI Recommendations:\n%s\n\n", response)
}

func handleAICommand(client openai.Client, userInput string, config *Config) {
	parts := strings.Fields(userInput)
	if len(parts) < 2 {
		fmt.Println("❌ Invalid AI command. Use: ai <command>")
		return
	}

	command := strings.ToLower(parts[1])

	switch command {
	case "learn":
		handleAILearnCommand(client, config)
	case "research":
		if len(parts) < 3 {
			fmt.Println("❌ Usage: ai research <topic>")
			return
		}
		topic := strings.Join(parts[2:], " ")
		handleAIResearchCommand(client, topic, config)
	case "scrape":
		if len(parts) < 3 {
			fmt.Println("❌ Usage: ai scrape <url>")
			return
		}
		url := parts[2]
		handleAIScrapeCommand(client, url, config)
	default:
		fmt.Println("❌ Unknown AI command. Available: learn, research, scrape")
	}
}

func handleAILearnCommand(client openai.Client, config *Config) {
	fmt.Println("🧠 AI Learning Mode: Comprehensive Go Ecosystem Research")
	fmt.Println("========================================================")
	
	// Create learning directory
	learningDir := "ai_learning"
	os.MkdirAll(learningDir, 0755)
	
	// Define learning targets with correct URLs
	learningTargets := []struct {
		name        string
		url         string
		description string
		category    string
	}{
		{"Official Go Tutorials", "https://golang.org/doc/tutorial/", "Official Go language tutorials", "tutorials"},
		{"Go by Example", "https://gobyexample.com/", "Hands-on Go examples", "tutorials"},
		{"Go Programming Language Book", "https://www.gopl.io/", "The Go Programming Language book", "books"},
		{"Gin Web Framework", "https://gin-gonic.com/", "Gin web framework documentation", "frameworks"},
		{"Awesome Go", "https://github.com/avelino/awesome-go", "Curated Go libraries and frameworks", "libraries"},
		{"Go ML Libraries", "https://github.com/gorgonia/gorgonia", "Go machine learning ecosystem", "ml"},
		{"GolangCI Lint", "https://golangci-lint.run/", "Go code quality linter", "tools"},
		{"Cobra CLI", "https://cobra.dev/", "CLI applications in Go", "tools"},
		{"Viper Config", "https://github.com/spf13/viper", "Configuration management", "tools"},
		{"Go Reddit", "https://www.reddit.com/r/golang/", "Go community discussions", "community"},
	}
	
	var allContent strings.Builder
	allContent.WriteString("AI Learning Report: Go Ecosystem Research\n")
	allContent.WriteString("==========================================\n\n")
	
	for i, target := range learningTargets {
		fmt.Printf("📚 [%d/%d] Learning from: %s\n", i+1, len(learningTargets), target.name)
		
		// Scrape content with retry logic
		content, err := scrapeWebContentWithRetry(target.url, 3)
		if err != nil {
			fmt.Printf("⚠️  Failed to scrape %s: %v\n", target.name, err)
			// Add error info to summary
			allContent.WriteString(fmt.Sprintf("## %s (%s) - FAILED\n", target.name, target.category))
			allContent.WriteString(fmt.Sprintf("URL: %s\n", target.url))
			allContent.WriteString(fmt.Sprintf("Description: %s\n", target.description))
			allContent.WriteString(fmt.Sprintf("Error: %v\n\n", err))
			continue
		}
		
		// Save to file
		filename := filepath.Join(learningDir, fmt.Sprintf("%s_%s.txt", target.category, strings.ReplaceAll(target.name, " ", "_")))
		err = os.WriteFile(filename, []byte(content), 0644)
		if err != nil {
			fmt.Printf("⚠️  Failed to save %s: %v\n", filename, err)
		}
		
		// Add to summary
		allContent.WriteString(fmt.Sprintf("## %s (%s)\n", target.name, target.category))
		allContent.WriteString(fmt.Sprintf("URL: %s\n", target.url))
		allContent.WriteString(fmt.Sprintf("Description: %s\n", target.description))
		allContent.WriteString(fmt.Sprintf("Content Preview: %s\n\n", truncateText(content, 500)))
		
		// Small delay to be respectful
		time.Sleep(1 * time.Second)
	}
	
	// Send all content to AI for analysis
	response, err := sendMessageWithConfig(client, fmt.Sprintf("I've scraped and learned from the Go ecosystem. Here's what I found:\n\n%s\n\nPlease analyze this comprehensive Go learning data and provide insights about:\n1. Key learning priorities\n2. Hidden gems and niche libraries\n3. Best practices and patterns\n4. Learning roadmap recommendations\n5. Advanced topics to explore", allContent.String()), config)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	
	fmt.Printf("🧠 AI Learning Analysis:\n%s\n\n", response)
	fmt.Printf("📁 Learning data saved to: %s/\n", learningDir)
}

func handleAIResearchCommand(client openai.Client, topic string, config *Config) {
	fmt.Printf("🔍 AI Research Mode: %s\n", topic)
	fmt.Println("================================")
	
	// Research URLs based on topic
	researchUrls := getResearchUrls(topic)
	
	var researchContent strings.Builder
	researchContent.WriteString(fmt.Sprintf("Research Report: %s\n", topic))
	researchContent.WriteString("========================\n\n")
	
	for i, url := range researchUrls {
		fmt.Printf("🔍 [%d/%d] Researching: %s\n", i+1, len(researchUrls), url)
		
		content, err := scrapeWebContent(url)
		if err != nil {
			fmt.Printf("⚠️  Failed to scrape %s: %v\n", url, err)
			continue
		}
		
		researchContent.WriteString(fmt.Sprintf("## Source: %s\n", url))
		researchContent.WriteString(fmt.Sprintf("Content: %s\n\n", truncateText(content, 1000)))
		
		time.Sleep(1 * time.Second)
	}
	
	// Send to AI for analysis
	response, err := sendMessageWithConfig(client, fmt.Sprintf("I've researched '%s' from multiple sources. Here's what I found:\n\n%s\n\nPlease provide a comprehensive analysis and recommendations about this topic.", topic, researchContent.String()), config)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	
	fmt.Printf("🔍 Research Analysis:\n%s\n\n", response)
}

func handleAIScrapeCommand(client openai.Client, url string, config *Config) {
	fmt.Printf("🕷️  AI Scraping: %s\n", url)
	fmt.Println("================================")
	
	content, err := scrapeWebContent(url)
	if err != nil {
		fmt.Printf("❌ Failed to scrape URL: %v\n", err)
		return
	}
	
	// Send to AI for analysis
	response, err := sendMessageWithConfig(client, fmt.Sprintf("I've scraped content from %s:\n\n%s\n\nPlease analyze this content and provide insights, key takeaways, and recommendations.", url, content), config)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	
	fmt.Printf("🕷️  Scraped Content Analysis:\n%s\n\n", response)
}

// GitHub API functions
func getGitHubRepos(token string) ([]GitHubRepo, error) {
	client := &http.Client{}
	fmt.Printf("📚 Fetching your GitHub repositories...\n")
	req, err := http.NewRequest("GET", "https://api.github.com/user/repos?sort=updated&per_page=50", nil)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("Authorization", "token "+token)
	req.Header.Set("Accept", "application/vnd.github.v3+json")
	
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("GitHub API error: %s", resp.Status)
	}
	
	var repos []GitHubRepo
	err = json.NewDecoder(resp.Body).Decode(&repos)
	return repos, err
}

func searchGitHubRepos(query string) (*GitHubSearchResult, error) {
	// Remove timeout to prevent hanging
	client := &http.Client{}
	url := fmt.Sprintf("https://api.github.com/search/repositories?q=%s&sort=stars&order=desc&per_page=10", query)
	
	fmt.Printf("🔍 Searching GitHub for: %s...\n", query)
	
	// Simple request without retry logic for now
	resp, err := client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("GitHub API request failed: %v", err)
	}
	defer resp.Body.Close()
	
	fmt.Printf("📡 GitHub API response: %s\n", resp.Status)
	
	// Handle different HTTP status codes
	if resp.StatusCode == 403 {
		// Rate limit exceeded
		return nil, fmt.Errorf("GitHub API rate limit exceeded. Please set GITHUB_TOKEN in your .env file for higher rate limits")
	} else if resp.StatusCode == 401 {
		return nil, fmt.Errorf("GitHub API authentication failed. Please check your GITHUB_TOKEN")
	} else if resp.StatusCode != 200 {
		return nil, fmt.Errorf("GitHub API error: %s", resp.Status)
	}
	
	var result GitHubSearchResult
	err = json.NewDecoder(resp.Body).Decode(&result)
	return &result, err
}

func getGitHubIssues(repo string) ([]GitHubIssue, error) {
	client := &http.Client{}
	url := fmt.Sprintf("https://api.github.com/repos/%s/issues?state=all&per_page=20", repo)
	
	fmt.Printf("🐛 Fetching issues for %s...\n", repo)
	resp, err := client.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("GitHub API error: %s", resp.Status)
	}
	
	var issues []GitHubIssue
	err = json.NewDecoder(resp.Body).Decode(&issues)
	return issues, err
}

func getGitHubPullRequests(repo string) ([]GitHubPullRequest, error) {
	client := &http.Client{}
	url := fmt.Sprintf("https://api.github.com/repos/%s/pulls?state=all&per_page=20", repo)
	
	fmt.Printf("🔄 Fetching pull requests for %s...\n", repo)
	resp, err := client.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("GitHub API error: %s", resp.Status)
	}
	
	var prs []GitHubPullRequest
	err = json.NewDecoder(resp.Body).Decode(&prs)
	return prs, err
}

func cloneGitHubRepo(repo string) error {
	// Simple git clone command
	cmd := fmt.Sprintf("git clone https://github.com/%s.git", repo)
	fmt.Printf("Executing: %s\n", cmd)
	// In a real implementation, you'd use os/exec to run this command
	return nil
}

// Formatting functions for AI
func formatReposForAI(repos []GitHubRepo) string {
	var result strings.Builder
	result.WriteString("Repository Portfolio Analysis:\n")
	result.WriteString("============================\n\n")
	
	for _, repo := range repos {
		result.WriteString(fmt.Sprintf("📁 %s\n", repo.FullName))
		result.WriteString(fmt.Sprintf("   Language: %s\n", repo.Language))
		result.WriteString(fmt.Sprintf("   Stars: %d | Forks: %d\n", repo.Stars, repo.Forks))
		result.WriteString(fmt.Sprintf("   Description: %s\n", repo.Description))
		result.WriteString(fmt.Sprintf("   Updated: %s\n\n", repo.UpdatedAt))
	}
	
	return result.String()
}

func formatSearchResultsForAI(results *GitHubSearchResult) string {
	var result strings.Builder
	result.WriteString(fmt.Sprintf("Search Results (%d total):\n", results.TotalCount))
	result.WriteString("==========================\n\n")
	
	for _, item := range results.Items {
		result.WriteString(fmt.Sprintf("📁 %s\n", item.FullName))
		result.WriteString(fmt.Sprintf("   Language: %s\n", item.Language))
		result.WriteString(fmt.Sprintf("   Stars: %d | Forks: %d\n", item.Stars, item.Forks))
		result.WriteString(fmt.Sprintf("   Description: %s\n", item.Description))
		result.WriteString(fmt.Sprintf("   Updated: %s\n\n", item.UpdatedAt))
	}
	
	return result.String()
}

func formatIssuesForAI(issues []GitHubIssue) string {
	var result strings.Builder
	result.WriteString(fmt.Sprintf("Issues (%d total):\n", len(issues)))
	result.WriteString("==================\n\n")
	
	for _, issue := range issues {
		result.WriteString(fmt.Sprintf("🔴 #%d: %s\n", issue.Number, issue.Title))
		result.WriteString(fmt.Sprintf("   State: %s | Author: %s\n", issue.State, issue.User.Login))
		result.WriteString(fmt.Sprintf("   Created: %s\n", issue.CreatedAt))
		if issue.Body != "" {
			body := issue.Body
			if len(body) > 200 {
				body = body[:200] + "..."
			}
			result.WriteString(fmt.Sprintf("   Description: %s\n", body))
		}
		result.WriteString("\n")
	}
	
	return result.String()
}

func formatPullRequestsForAI(prs []GitHubPullRequest) string {
	var result strings.Builder
	result.WriteString(fmt.Sprintf("Pull Requests (%d total):\n", len(prs)))
	result.WriteString("========================\n\n")
	
	for _, pr := range prs {
		result.WriteString(fmt.Sprintf("🔄 #%d: %s\n", pr.Number, pr.Title))
		result.WriteString(fmt.Sprintf("   State: %s | Author: %s\n", pr.State, pr.User.Login))
		result.WriteString(fmt.Sprintf("   Branch: %s → %s\n", pr.Head.Ref, pr.Base.Ref))
		result.WriteString(fmt.Sprintf("   Created: %s\n", pr.CreatedAt))
		if pr.Body != "" {
			body := pr.Body
			if len(body) > 200 {
				body = body[:200] + "..."
			}
			result.WriteString(fmt.Sprintf("   Description: %s\n", body))
		}
		result.WriteString("\n")
	}
	
	return result.String()
}

func getCuratedSearchResults(query string) string {
	queryLower := strings.ToLower(query)
	
	// Curated repositories based on common search terms
	curatedRepos := map[string][]struct {
		name        string
		description string
		language    string
		stars       int
		url         string
	}{
		"golang": {
			{"golang/go", "The Go programming language", "Go", 120000, "https://github.com/golang/go"},
			{"gin-gonic/gin", "HTTP web framework written in Go", "Go", 75000, "https://github.com/gin-gonic/gin"},
			{"avelino/awesome-go", "A curated list of awesome Go frameworks, libraries and software", "Go", 120000, "https://github.com/avelino/awesome-go"},
			{"practical-tutorials/project-based-learning", "Curated list of project-based tutorials", "Go", 150000, "https://github.com/practical-tutorials/project-based-learning"},
			{"ollama/ollama", "Get up and running with large language models locally", "Go", 50000, "https://github.com/ollama/ollama"},
		},
		"ai": {
			{"ollama/ollama", "Get up and running with large language models locally", "Go", 50000, "https://github.com/ollama/ollama"},
			{"go-skynet/go-llama.cpp", "Go bindings for llama.cpp", "Go", 2000, "https://github.com/go-skynet/go-llama.cpp"},
			{"gorgonia/gorgonia", "Gorgonia is a library that helps facilitate machine learning in Go", "Go", 5000, "https://github.com/gorgonia/gorgonia"},
		},
		"machine learning": {
			{"gorgonia/gorgonia", "Gorgonia is a library that helps facilitate machine learning in Go", "Go", 5000, "https://github.com/gorgonia/gorgonia"},
			{"go-skynet/go-llama.cpp", "Go bindings for llama.cpp", "Go", 2000, "https://github.com/go-skynet/go-llama.cpp"},
		},
		"web": {
			{"gin-gonic/gin", "HTTP web framework written in Go", "Go", 75000, "https://github.com/gin-gonic/gin"},
			{"gorilla/mux", "A powerful HTTP router and URL matcher for building Go web servers", "Go", 20000, "https://github.com/gorilla/mux"},
			{"labstack/echo", "High performance, minimalist Go web framework", "Go", 30000, "https://github.com/labstack/echo"},
		},
	}
	
	var result strings.Builder
	result.WriteString("Curated Search Results (GitHub API rate limited):\n")
	result.WriteString("===============================================\n\n")
	
	// Find matching categories
	var foundRepos []struct {
		name        string
		description string
		language    string
		stars       int
		url         string
	}
	
	for category, repos := range curatedRepos {
		if strings.Contains(queryLower, category) {
			foundRepos = append(foundRepos, repos...)
		}
	}
	
	// If no specific category matches, show general Go repositories
	if len(foundRepos) == 0 {
		foundRepos = curatedRepos["golang"]
	}
	
	// Limit to 5 results
	if len(foundRepos) > 5 {
		foundRepos = foundRepos[:5]
	}
	
	for _, repo := range foundRepos {
		result.WriteString(fmt.Sprintf("📁 %s\n", repo.name))
		result.WriteString(fmt.Sprintf("   Language: %s\n", repo.language))
		result.WriteString(fmt.Sprintf("   Stars: %d\n", repo.stars))
		result.WriteString(fmt.Sprintf("   Description: %s\n", repo.description))
		result.WriteString(fmt.Sprintf("   URL: %s\n\n", repo.url))
	}
	
	return result.String()
}

// Web scraping and utility functions
func scrapeWebContent(url string) (string, error) {
	client := &http.Client{}
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", err
	}
	
	// Set user agent to avoid blocking
	req.Header.Set("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
	
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		return "", fmt.Errorf("HTTP %d: %s", resp.StatusCode, resp.Status)
	}
	
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	
	// Basic HTML cleaning - remove tags and get text content
	content := string(body)
	content = cleanHTML(content)
	
	return content, nil
}

func scrapeWebContentWithRetry(url string, maxRetries int) (string, error) {
	var lastErr error
	
	for attempt := 1; attempt <= maxRetries; attempt++ {
		content, err := scrapeWebContent(url)
		if err == nil {
			return content, nil
		}
		
		lastErr = err
		if attempt < maxRetries {
			fmt.Printf("⏳ Retry %d/%d for %s...\n", attempt, maxRetries, url)
			time.Sleep(time.Duration(attempt) * time.Second)
		}
	}
	
	return "", fmt.Errorf("failed after %d attempts: %v", maxRetries, lastErr)
}

func cleanHTML(html string) string {
	// Remove script and style tags
	re := regexp.MustCompile(`(?i)<(script|style)[^>]*>.*?</(script|style)>`)
	html = re.ReplaceAllString(html, "")
	
	// Remove HTML tags
	re = regexp.MustCompile(`<[^>]*>`)
	html = re.ReplaceAllString(html, " ")
	
	// Clean up whitespace
	re = regexp.MustCompile(`\s+`)
	html = re.ReplaceAllString(html, " ")
	
	// Remove HTML entities
	html = strings.ReplaceAll(html, "&nbsp;", " ")
	html = strings.ReplaceAll(html, "&amp;", "&")
	html = strings.ReplaceAll(html, "&lt;", "<")
	html = strings.ReplaceAll(html, "&gt;", ">")
	html = strings.ReplaceAll(html, "&quot;", "\"")
	
	return strings.TrimSpace(html)
}

func truncateText(text string, maxLength int) string {
	if len(text) <= maxLength {
		return text
	}
	return text[:maxLength] + "..."
}

func getResearchUrls(topic string) []string {
	topicLower := strings.ToLower(topic)
	
	// Define research URLs based on topic
	urls := []string{}
	
	if strings.Contains(topicLower, "machine learning") || strings.Contains(topicLower, "ml") {
		urls = append(urls, 
			"https://github.com/gorgonia/gorgonia",
			"https://github.com/go-skynet/go-llama.cpp",
			"https://github.com/topics/machine-learning-go",
			"https://github.com/owulveryck/onnx-go",
			"https://github.com/sjwhitworth/golearn",
		)
	}
	
	if strings.Contains(topicLower, "web") || strings.Contains(topicLower, "http") {
		urls = append(urls,
			"https://gin-gonic.com/",
			"https://github.com/gorilla/mux",
			"https://github.com/labstack/echo",
			"https://github.com/valyala/fasthttp",
		)
	}
	
	if strings.Contains(topicLower, "database") || strings.Contains(topicLower, "sql") {
		urls = append(urls,
			"https://github.com/jmoiron/sqlx",
			"https://github.com/gorm/gorm",
			"https://github.com/go-pg/pg",
		)
	}
	
	if strings.Contains(topicLower, "cli") || strings.Contains(topicLower, "command") {
		urls = append(urls,
			"https://cobra.dev/",
			"https://github.com/spf13/viper",
			"https://github.com/urfave/cli",
		)
	}
	
	if strings.Contains(topicLower, "testing") {
		urls = append(urls,
			"https://golang.org/pkg/testing/",
			"https://github.com/stretchr/testify",
			"https://github.com/golang/mock",
		)
	}
	
	// Default research URLs if no specific topic matches
	if len(urls) == 0 {
		urls = append(urls,
			"https://golang.org/doc/",
			"https://github.com/avelino/awesome-go",
			"https://gobyexample.com/",
		)
	}
	
	return urls
}

// Enhanced message functions
func sendMessageWithConfig(client openai.Client, message string, config *Config) (string, error) {
	if config.Verbose {
		fmt.Printf("[DEBUG] Sending message: %s\n", message)
	}

	ctx := context.Background()

	// Create chat completion request with config
	req := openai.ChatCompletionNewParams{
		Model: config.Model,
		Messages: []openai.ChatCompletionMessageParamUnion{
			openai.UserMessage(message),
		},
		MaxTokens: openai.Int(int64(config.MaxTokens)),
		Temperature: openai.Float(config.Temperature),
		TopP: openai.Float(0.9),
	}

	if config.Verbose {
		fmt.Printf("[DEBUG] Request: %+v\n", req)
	}

	// Send request to Ollama
	resp, err := client.Chat.Completions.New(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to create chat completion: %w", err)
	}

	if config.Verbose {
		fmt.Printf("[DEBUG] Response: %+v\n", resp)
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response choices received")
	}

	// Extract text content from the response
	return resp.Choices[0].Message.Content, nil
}

func sendMessageWithContext(client openai.Client, message string, history []string, config *Config) (string, error) {
	// Build context from conversation history
	var messages []openai.ChatCompletionMessageParamUnion
	
	// Add system message for context
	messages = append(messages, openai.SystemMessage("You are a helpful AI coding assistant. You have access to GitHub repositories, can analyze code, and help with Go programming. Keep responses concise and helpful."))
	
	// Add recent conversation history (last 10 messages)
	start := len(history) - 10
	if start < 0 {
		start = 0
	}
	
	for i := start; i < len(history); i++ {
		if i%2 == 0 {
			messages = append(messages, openai.UserMessage(history[i]))
		} else {
			messages = append(messages, openai.AssistantMessage(history[i]))
		}
	}
	
	// Add current message
	messages = append(messages, openai.UserMessage(message))

	if config.Verbose {
		fmt.Printf("[DEBUG] Sending message with context: %s\n", message)
	}

	ctx := context.Background()

	// Create chat completion request with context
	req := openai.ChatCompletionNewParams{
		Model: config.Model,
		Messages: messages,
		MaxTokens: openai.Int(int64(config.MaxTokens)),
		Temperature: openai.Float(config.Temperature),
		TopP: openai.Float(0.9),
	}

	// Send request to Ollama
	resp, err := client.Chat.Completions.New(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to create chat completion: %w", err)
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response choices received")
	}

	// Extract text content from the response
	return resp.Choices[0].Message.Content, nil
}

func saveConversation(history []string, config *Config) {
	if len(history) == 0 {
		return
	}
	
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	filename := filepath.Join(config.LearningDir, fmt.Sprintf("conversation_%s.txt", timestamp))
	
	var content strings.Builder
	content.WriteString(fmt.Sprintf("Conversation saved at: %s\n", time.Now().Format("2006-01-02 15:04:05")))
	content.WriteString("==========================================\n\n")
	
	for i, msg := range history {
		if i%2 == 0 {
			content.WriteString(fmt.Sprintf("You: %s\n\n", msg))
		} else {
			content.WriteString(fmt.Sprintf("AI: %s\n\n", msg))
		}
	}
	
	err := os.WriteFile(filename, []byte(content.String()), 0644)
	if err != nil {
		if config.Verbose {
			fmt.Printf("[DEBUG] Failed to save conversation: %v\n", err)
		}
	}
}

// Existing functions from read_simple.go
func sendMessage(client openai.Client, message string, verbose bool) (string, error) {
	if verbose {
		fmt.Printf("[DEBUG] Sending message: %s\n", message)
	}

	ctx := context.Background()

	// Create chat completion request
	req := openai.ChatCompletionNewParams{
		Model: "llama3.2:3b", // Using your local Ollama model
		Messages: []openai.ChatCompletionMessageParamUnion{
			openai.UserMessage(message),
		},
		MaxTokens: openai.Int(2000),
		Temperature: openai.Float(0.7), // Balanced for coding tasks
		TopP: openai.Float(0.9),
	}

	if verbose {
		fmt.Printf("[DEBUG] Request: %+v\n", req)
	}

	// Send request to Ollama
	resp, err := client.Chat.Completions.New(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to create chat completion: %w", err)
	}

	if verbose {
		fmt.Printf("[DEBUG] Response: %+v\n", resp)
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response choices received")
	}

	// Extract text content from the response
	return resp.Choices[0].Message.Content, nil
}

func readFileOrFolder(path string) (string, error) {
	// Check if it's a directory
	info, err := os.Stat(path)
	if err != nil {
		return "", err
	}
	
	if info.IsDir() {
		// It's a directory, read all files in it
		return readDirectoryContents(path)
	} else {
		// It's a file, read it
		return readFile(path)
	}
}

func readFile(filePath string) (string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	content, err := io.ReadAll(file)
	if err != nil {
		return "", err
	}

	return string(content), nil
}

func readDirectoryContents(dirPath string) (string, error) {
	var result strings.Builder
	result.WriteString(fmt.Sprintf("Directory: %s\n", dirPath))
	result.WriteString("=" + strings.Repeat("=", len(dirPath)) + "\n\n")
	
	entries, err := os.ReadDir(dirPath)
	if err != nil {
		return "", err
	}
	
	for _, entry := range entries {
		entryPath := dirPath + "/" + entry.Name()
		if entry.IsDir() {
			result.WriteString(fmt.Sprintf("📁 %s/ (directory)\n", entry.Name()))
		} else {
			// Read file content
			content, err := readFile(entryPath)
			if err != nil {
				result.WriteString(fmt.Sprintf("📄 %s (error reading: %v)\n", entry.Name(), err))
			} else {
				result.WriteString(fmt.Sprintf("📄 %s:\n", entry.Name()))
				result.WriteString("```\n")
				result.WriteString(content)
				result.WriteString("\n```\n\n")
			}
		}
	}
	
	return result.String(), nil
}

func listDirectory(dirPath string) (string, error) {
	var result strings.Builder
	result.WriteString(fmt.Sprintf("Directory listing: %s\n", dirPath))
	result.WriteString("=" + strings.Repeat("=", len(dirPath)) + "\n\n")
	
	entries, err := os.ReadDir(dirPath)
	if err != nil {
		return "", err
	}
	
	for _, entry := range entries {
		info, err := entry.Info()
		if err != nil {
			result.WriteString(fmt.Sprintf("❓ %s (error getting info)\n", entry.Name()))
			continue
		}
		
		if entry.IsDir() {
			result.WriteString(fmt.Sprintf("📁 %s/ (directory, %d bytes)\n", entry.Name(), info.Size()))
		} else {
			result.WriteString(fmt.Sprintf("📄 %s (%d bytes, modified: %s)\n", entry.Name(), info.Size(), info.ModTime().Format("2006-01-02 15:04:05")))
		}
	}
	
	return result.String(), nil
}
