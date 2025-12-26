/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: list_files.go                                                         ║
║  Generated: 2025-12-26T10:00:42.390753                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - LIST_FILES.GO
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
	"os"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

// Tool definitions
type Tool struct {
	Type     string                 `json:"type"`
	Function ToolFunction           `json:"function"`
}

type ToolFunction struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
}

// Tool call structures
type ToolCallArguments struct {
	FilePath string `json:"file_path"`
	DirPath  string `json:"dir_path"`
}

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}

	apiKey := os.Getenv("AIMLAPI_API_KEY")
	if apiKey == "" {
		log.Fatal("AIMLAPI_API_KEY environment variable is required")
	}

	// Create OpenAI client with AIMLAPI base URL
	client := openai.NewClient(
		option.WithAPIKey(apiKey),
		option.WithBaseURL("https://api.aimlapi.com/v1"),
	)

	// Check for verbose flag
	verbose := len(os.Args) > 1 && os.Args[1] == "--verbose"

	fmt.Println("🤖 Coding Agent Workshop - File Explorer")
	fmt.Println("Now Claude can read files AND list directories!")
	fmt.Println("Try: 'List all files in this folder' or 'What's in fizzbuzz.js?'")
	fmt.Println("Type 'quit' or 'exit' to stop")
	fmt.Println()

	scanner := bufio.NewScanner(os.Stdin)

	for {
		fmt.Print("You: ")
		if !scanner.Scan() {
			break
		}

		userInput := strings.TrimSpace(scanner.Text())
		if userInput == "" {
			continue
		}

		if userInput == "quit" || userInput == "exit" {
			fmt.Println("Goodbye!")
			break
		}

		// Send message to Claude via AIMLAPI with tools
		response, err := sendMessageWithTools(client, userInput, verbose)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			continue
		}

		fmt.Printf("Claude: %s\n\n", response)
	}
}

func sendMessageWithTools(client *openai.Client, message string, verbose bool) (string, error) {
	if verbose {
		fmt.Printf("[DEBUG] Sending message: %s\n", message)
	}

	ctx := context.Background()

	// Define available tools
	tools := []Tool{
		{
			Type: "function",
			Function: ToolFunction{
				Name:        "read_file",
				Description: "Read the contents of a file",
				Parameters: map[string]interface{}{
					"type": "object",
					"properties": map[string]interface{}{
						"file_path": map[string]interface{}{
							"type":        "string",
							"description": "The path to the file to read",
						},
					},
					"required": []string{"file_path"},
				},
			},
		},
		{
			Type: "function",
			Function: ToolFunction{
				Name:        "list_files",
				Description: "List files and directories in a given path",
				Parameters: map[string]interface{}{
					"type": "object",
					"properties": map[string]interface{}{
						"dir_path": map[string]interface{}{
							"type":        "string",
							"description": "The directory path to list (use '.' for current directory)",
						},
					},
					"required": []string{"dir_path"},
				},
			},
		},
	}

	// Create chat completion request with tools
	req := openai.ChatCompletionRequest{
		Model: "anthropic/claude-3-5-sonnet-20240620",
		Messages: []openai.ChatCompletionMessage{
			{
				Role:    openai.ChatCompletionMessageRoleUser,
				Content: message,
			},
		},
		Tools:     tools,
		MaxTokens: 2000,
	}

	if verbose {
		fmt.Printf("[DEBUG] Request: %+v\n", req)
	}

	// Send request to AIMLAPI
	resp, err := client.Chat.Completions.Create(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to create chat completion: %w", err)
	}

	if verbose {
		fmt.Printf("[DEBUG] Response: %+v\n", resp)
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response choices received")
	}

	choice := resp.Choices[0]
	
	// Check if Claude wants to use a tool
	if len(choice.Message.ToolCalls) > 0 {
		return handleToolCalls(client, choice.Message.ToolCalls, verbose)
	}

	return choice.Message.Content, nil
}

func handleToolCalls(client *openai.Client, toolCalls []openai.ChatCompletionMessageToolCall, verbose bool) (string, error) {
	ctx := context.Background()
	
	// Process each tool call
	var messages []openai.ChatCompletionMessage

	for _, toolCall := range toolCalls {
		if verbose {
			fmt.Printf("[DEBUG] Tool call: %s with args: %s\n", toolCall.Function.Name, toolCall.Function.Arguments)
		}

		var result string
		var err error

		switch toolCall.Function.Name {
		case "read_file":
			var args ToolCallArguments
			if err := json.Unmarshal([]byte(toolCall.Function.Arguments), &args); err != nil {
				result = fmt.Sprintf("Error parsing arguments: %v", err)
			} else {
				result, err = readFile(args.FilePath)
				if err != nil {
					result = fmt.Sprintf("Error reading file: %v", err)
				}
			}
		case "list_files":
			var args ToolCallArguments
			if err := json.Unmarshal([]byte(toolCall.Function.Arguments), &args); err != nil {
				result = fmt.Sprintf("Error parsing arguments: %v", err)
			} else {
				result, err = listFiles(args.DirPath)
				if err != nil {
					result = fmt.Sprintf("Error listing files: %v", err)
				}
			}
		default:
			result = fmt.Sprintf("Unknown tool: %s", toolCall.Function.Name)
		}

		// Add tool result to messages
		messages = append(messages, openai.ChatCompletionMessage{
			Role:       openai.ChatCompletionMessageRoleTool,
			Content:    result,
			ToolCallID: toolCall.ID,
		})
	}

	// Send tool results back to Claude
	req := openai.ChatCompletionRequest{
		Model: "anthropic/claude-3-5-sonnet-20240620",
		Messages: messages,
		MaxTokens: 2000,
	}

	if verbose {
		fmt.Printf("[DEBUG] Tool results request: %+v\n", req)
	}

	resp, err := client.Chat.Completions.Create(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to process tool results: %w", err)
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response choices received")
	}

	return resp.Choices[0].Message.Content, nil
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

func listFiles(dirPath string) (string, error) {
	// Handle relative paths
	if dirPath == "." {
		dirPath = "."
	}

	// Read directory contents
	entries, err := os.ReadDir(dirPath)
	if err != nil {
		return "", err
	}

	var result strings.Builder
	result.WriteString(fmt.Sprintf("Contents of directory '%s':\n", dirPath))
	result.WriteString("Type\tName\tSize\n")
	result.WriteString("----\t----\t----\n")

	for _, entry := range entries {
		entryType := "file"
		if entry.IsDir() {
			entryType = "dir "
		}

		// Get file size
		info, err := entry.Info()
		size := "N/A"
		if err == nil {
			if entry.IsDir() {
				size = "-"
			} else {
				size = fmt.Sprintf("%d bytes", info.Size())
			}
		}

		result.WriteString(fmt.Sprintf("%s\t%s\t%s\n", entryType, entry.Name(), size))
	}

	return result.String(), nil
}
