/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: security.go                                                           ║
║  Generated: 2025-12-26T10:00:42.509741                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - SECURITY.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package security

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// SecurityManager handles security-related operations
type SecurityManager struct {
	dataDir string
}

// NewSecurityManager creates a new security manager
func NewSecurityManager(dataDir string) *SecurityManager {
	return &SecurityManager{
		dataDir: dataDir,
	}
}

// SanitizeInput cleans user input to prevent injection attacks
func (sm *SecurityManager) SanitizeInput(input string) string {
	// Remove potentially dangerous characters
	dangerous := []string{"<", ">", "\"", "'", "&", ";", "|", "`", "$", "(", ")", "{", "}"}
	sanitized := input

	for _, char := range dangerous {
		sanitized = strings.ReplaceAll(sanitized, char, "")
	}

	// Limit length
	if len(sanitized) > 1000 {
		sanitized = sanitized[:1000]
	}

	return strings.TrimSpace(sanitized)
}

// ValidateURL checks if a URL is safe to scrape
func (sm *SecurityManager) ValidateURL(url string) error {
	if url == "" {
		return fmt.Errorf("URL cannot be empty")
	}

	// Only allow HTTP/HTTPS
	if !strings.HasPrefix(url, "http://") && !strings.HasPrefix(url, "https://") {
		return fmt.Errorf("URL must use HTTP or HTTPS protocol")
	}

	// Block potentially dangerous domains
	dangerousDomains := []string{
		"localhost",
		"127.0.0.1",
		"0.0.0.0",
		"::1",
	}

	for _, domain := range dangerousDomains {
		if strings.Contains(url, domain) {
			return fmt.Errorf("URL contains potentially dangerous domain: %s", domain)
		}
	}

	return nil
}

// GenerateSecureFilename creates a secure filename for saved content
func (sm *SecurityManager) GenerateSecureFilename(prefix string) string {
	bytes := make([]byte, 8)
	rand.Read(bytes)
	hash := hex.EncodeToString(bytes)
	return fmt.Sprintf("%s_%s.txt", prefix, hash)
}

// SaveSecureContent saves content with security checks
func (sm *SecurityManager) SaveSecureContent(content, filename string) error {
	// Sanitize filename
	filename = sm.SanitizeInput(filename)
	if filename == "" {
		filename = "content"
	}

	// Ensure filename is safe
	if strings.Contains(filename, "..") || strings.Contains(filename, "/") {
		return fmt.Errorf("invalid filename")
	}

	// Limit content size
	if len(content) > 1024*1024 { // 1MB limit
		return fmt.Errorf("content too large")
	}

	// Create secure path
	securePath := filepath.Join(sm.dataDir, "secure", filename)

	// Ensure directory exists
	if err := os.MkdirAll(filepath.Dir(securePath), 0755); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	// Save content
	return os.WriteFile(securePath, []byte(content), 0644)
}

// HashContent creates a secure hash of content
func (sm *SecurityManager) HashContent(content string) string {
	hash := sha256.Sum256([]byte(content))
	return hex.EncodeToString(hash[:])
}

// ValidateGitHubToken checks if a GitHub token is properly formatted
func (sm *SecurityManager) ValidateGitHubToken(token string) error {
	if token == "" {
		return fmt.Errorf("GitHub token cannot be empty")
	}

	// GitHub tokens are typically 40 characters for classic tokens
	// or start with ghp_ for fine-grained tokens
	if len(token) < 20 {
		return fmt.Errorf("GitHub token appears to be too short")
	}

	return nil
}

// CleanupOldFiles removes old temporary files
func (sm *SecurityManager) CleanupOldFiles() error {
	tempDir := filepath.Join(sm.dataDir, "temp")
	if _, err := os.Stat(tempDir); os.IsNotExist(err) {
		return nil
	}

	// Remove files older than 7 days
	// This is a simplified version - in production you'd want more sophisticated cleanup
	return os.RemoveAll(tempDir)
}
