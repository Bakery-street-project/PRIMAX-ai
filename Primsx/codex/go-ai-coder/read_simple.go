/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: read_simple.go                                                        ║
║  Generated: 2025-12-26T10:00:42.400835                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - READ_SIMPLE.GO
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
	"io"
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

	fmt.Println("🤖 Coding Agent Workshop - File Reader (Ollama)")
	fmt.Println("Using local Ollama model: llama3.2:3b")
	fmt.Println("Commands:")
	fmt.Println("  read <file_or_folder> - Read file content or all files in folder")
	fmt.Println("  list <directory> - List directory contents")
	fmt.Println("  quit/exit - Exit the program")
	fmt.Println()
	fmt.Println("Examples:")
	fmt.Println("  read fizzbuzz.js")
	fmt.Println("  read /home/booze/Documents/blackrockdata")
	fmt.Println("  list /home/booze/Documents")
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

		// Check if user wants to read a file or folder
		if strings.HasPrefix(strings.ToLower(userInput), "read ") {
			filePath := strings.TrimSpace(strings.TrimPrefix(userInput, "read "))
			filePath = strings.TrimSpace(strings.TrimPrefix(filePath, "Read "))
			content, err := readFileOrFolder(filePath)
			if err != nil {
				fmt.Printf("Error reading file/folder: %v\n", err)
				continue
			}
			
			// Send file content to AI for analysis
			response, err := sendMessage(client, fmt.Sprintf("Here is the content of %s:\n\n%s\n\nPlease analyze this and provide insights.", filePath, content), verbose)
			if err != nil {
				fmt.Printf("Error: %v\n", err)
				continue
			}
			fmt.Printf("AI: %s\n\n", response)
		} else if strings.HasPrefix(strings.ToLower(userInput), "list ") {
			// List directory contents
			dirPath := strings.TrimSpace(strings.TrimPrefix(userInput, "list "))
			dirPath = strings.TrimSpace(strings.TrimPrefix(dirPath, "List "))
			content, err := listDirectory(dirPath)
			if err != nil {
				fmt.Printf("Error listing directory: %v\n", err)
				continue
			}
			
			// Send directory listing to AI
			response, err := sendMessage(client, fmt.Sprintf("Here is the directory listing of %s:\n\n%s\n\nPlease analyze this directory structure and provide insights.", dirPath, content), verbose)
			if err != nil {
				fmt.Printf("Error: %v\n", err)
				continue
			}
			fmt.Printf("AI: %s\n\n", response)
		} else {
			// Regular chat
			response, err := sendMessage(client, userInput, verbose)
			if err != nil {
				fmt.Printf("Error: %v\n", err)
				continue
			}
			fmt.Printf("AI: %s\n\n", response)
		}
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
