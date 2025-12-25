// ==============================================================================
// PRIMSX CODEX - HUFFMAN_COMPRESS.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package codex_wheel

import (
	"container/heap"
	"sort"
)

type HuffmanNode struct {
	freq   int
	value  float64
	left   *HuffmanNode
	right  *HuffmanNode
}

type HuffmanHeap []*HuffmanNode

func (h HuffmanHeap) Len() int           { return len(h) }
func (h HuffmanHeap) Less(i, j int) bool { return h[i].freq < h[j].freq }
func (h HuffmanHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *HuffmanHeap) Push(x interface{}) { *h = append(*h, x.(*HuffmanNode)) }
func (h *HuffmanHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

func BuildHuffmanTree(data []float64) *HuffmanNode {
	freq := make(map[float64]int)
	for _, v := range data {
		freq[v]++
	}
	pq := make(HuffmanHeap, 0)
	heap.Init(&pq)
	for v, f := range freq {
		heap.Push(&pq, &HuffmanNode{freq: f, value: v})
	}
	for len(pq) > 1 {
		left := heap.Pop(&pq).(*HuffmanNode)
		right := heap.Pop(&pq).(*HuffmanNode)
		parent := &HuffmanNode{freq: left.freq + right.freq, left: left, right: right}
		heap.Push(&pq, parent)
	}
	return heap.Pop(&pq).(*HuffmanNode)
}

func HuffmanCodes(node *HuffmanNode, prefix string, codes map[float64]string) {
	if node == nil {
		return
	}
	if node.left == nil && node.right == nil {
		codes[node.value] = prefix
		return
	}
	HuffmanCodes(node.left, prefix+"0", codes)
	HuffmanCodes(node.right, prefix+"1", codes)
}

func CompressHuffman(trace map[string][]float64) map[float64]string {
	x := trace["x"]
	sort.Float64s(x)
	tree := BuildHuffmanTree(x)
	codes := make(map[float64]string)
	HuffmanCodes(tree, "", codes)
	return codes
}
