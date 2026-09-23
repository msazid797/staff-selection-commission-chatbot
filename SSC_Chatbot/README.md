# SSC Applicant Support Chatbot

An AI-powered FAQ chatbot prototype designed to assist applicants with SSC examination-related queries.

## Architecture

User → Web UI → FastAPI → RAG → FAISS → GPT-OSS-120B via Groq

## Features

- SSC FAQ-based question answering
- Retrieval-Augmented Generation (RAG)
- FAISS semantic search
- GPT-OSS-120B through Groq
- FastAPI backend
- Chat-style web interface
- Scrollable conversation history
- New Chat functionality
- Browser-based persistent chat history
- Exam selection
- Suggested questions
- Out-of-scope handling
- Responsive interface

## Technology Stack

- Python
- FastAPI
- LangChain
- FAISS
- Sentence Transformers
- Groq
- GPT-OSS-120B
- HTML
- CSS
- JavaScript

## Knowledge Base

SSC FAQ information is processed into embeddings and stored in a FAISS vector index.

## Prototype

This project is currently a prototype developed for demonstration purposes.