/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: chat.go                                                               ║
║  Generated: 2025-12-26T10:00:42.274483                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - CHAT.GO
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
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/joho/godotenv"
	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

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

	fmt.Println("🤖 Coding Agent Workshop - Basic Chat (Ollama)")
	fmt.Println("Using local Ollama model: llama3.2:3b")
	fmt.Println("Type 'quit' or 'exit' to stop")
	fmt.Println("Type '--verbose' as first argument for detailed logs")
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

		// Send message to Claude via AIMLAPI
		response, err := sendMessage(client, userInput, verbose)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			continue
		}

		fmt.Printf("Claude: %s\n\n", response)
	}
}

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
		MaxTokens: openai.Int(1000),
		Temperature: openai.Float(0.7), // Balanced for coding tasks
		TopP: openai.Float(0.9),
	}

	if verbose {
		fmt.Printf("[DEBUG] Request: %+v\n", req)
	}

	// Send request to AIMLAPI
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
