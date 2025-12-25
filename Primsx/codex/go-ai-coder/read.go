// ==============================================================================
// PRIMSX CODEX - READ.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

reapackage main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
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
type ToolCall struct {
	ID       string                 `json:"id"`
	Type     string                 `json:"type"`
	Function ToolCallFunction       `json:"function"`
}

type ToolCallFunction struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

type ToolCallArguments struct {
	FilePath string `json:"file_path"`
}

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}

	// No API key needed for Ollama - it runs locally

	// Create OpenAI client with Ollama base URL
	client := openai.NewClient(
		option.WithAPIKey("ollama"), // Dummy key, Ollama doesn't require authentication
		option.WithBaseURL("http://localhost:11434/v1"),
	)

	// Check for verbose flag
	verbose := len(os.Args) > 1 && os.Args[1] == "--verbose"

	fmt.Println("🤖 Coding Agent Workshop - File Reader (Ollama)")
	fmt.Println("Using local Ollama model: llama3.2:3b")
	fmt.Println("Now the AI can read files! Try: 'Read fizzbuzz.js'")
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

func sendMessageWithTools(client openai.Client, message string, verbose bool) (string, error) {
	if verbose {
		fmt.Printf("[DEBUG] Sending message: %s\n", message)
	}

	ctx := context.Background()

	// Define available tools
	tools := []openai.ChatCompletionToolParam{
		{
			Type: openai.F("function"),
			Function: openai.FunctionDefinition{
				Name:        openai.F("read_file"),
				Description: openai.F("Read the contents of a file"),
				Parameters: openai.F(`{
					"type": "object",
					"properties": {
						"file_path": {
							"type": "string",
							"description": "The path to the file to read"
						}
					},
					"required": ["file_path"]
				}`),
			},
		},
	}

	// Create chat completion request with tools
	req := openai.ChatCompletionNewParams{
		Model: "llama3.2:3b", // Using your local Ollama model
		Messages: []openai.ChatCompletionMessageParamUnion{
			openai.UserMessage(message),
		},
		Tools:     tools,
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

	choice := resp.Choices[0]
	
	// Check if Claude wants to use a tool
	if len(choice.Message.ToolCalls) > 0 {
		return handleToolCalls(client, choice.Message.ToolCalls, verbose)
	}

	return choice.Message.Content, nil
}

func handleToolCalls(client openai.Client, toolCalls []openai.ChatCompletionMessageToolCall, verbose bool) (string, error) {
	ctx := context.Background()
	
	// Process each tool call
	var messages []openai.ChatCompletionMessageParamUnion

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
		default:
			result = fmt.Sprintf("Unknown tool: %s", toolCall.Function.Name)
		}

		// Add tool result to messages
		messages = append(messages, openai.ToolMessage(result, toolCall.ID))
	}

	// Send tool results back to Ollama
	req := openai.ChatCompletionNewParams{
		Model: "llama3.2:3b", // Using your local Ollama model
		Messages: messages,
		MaxTokens: openai.Int(2000),
		Temperature: openai.Float(0.7),
		TopP: openai.Float(0.9),
	}

	if verbose {
		fmt.Printf("[DEBUG] Tool results request: %+v\n", req)
	}

	resp, err := client.Chat.Completions.New(ctx, req)
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
