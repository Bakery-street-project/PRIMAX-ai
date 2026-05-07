import { NextRequest, NextResponse } from 'next/server';

const PRIMAX_API_URL = process.env.NEXT_PUBLIC_PRIMAX_API_URL || 'http://localhost:8000';
const PRIMAX_API_KEY = process.env.PRIMAX_API_KEY;

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();

    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Call PRIMAX API
    const response = await fetch(`${PRIMAX_API_URL}/api/v1/ollama/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': PRIMAX_API_KEY || '',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('PRIMAX API error:', response.status, errorData);
      return NextResponse.json(
        { error: 'Failed to get response from PRIMAX AI' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}