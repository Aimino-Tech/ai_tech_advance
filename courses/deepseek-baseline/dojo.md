---
course: deepseek-baseline
title: DeepSeek V4 Flash Baseline
description: 10 smoke scenarios measuring base coding capability without skills
difficulty: smoke
model: deepseek-v4-flash
scenarios:
  - id: ds-01
    name: "Fix Python syntax error"
    description: "Fix missing colon in Python function definition"
    tags: [python, syntax]
    prompt: |
      Fix the syntax error in this Python function:

      ```python
      def greet(name)
          return f"Hello, {name}"
      ```
    expected_behaviors:
      - "Adds missing colon after function signature"
      - "Does not change the function body or logic"
    judge_criteria:
      - "Code compiles without syntax errors"
      - "greet('World') returns 'Hello, World'"

  - id: ds-02
    name: "TypeScript type annotations"
    description: "Add type annotations to an untyped TypeScript function"
    tags: [typescript, types]
    prompt: |
      Add proper TypeScript type annotations to this untyped function:

      ```typescript
      function calculateTotal(items, taxRate) {
        return items.reduce((sum, item) => {
          return sum + item.price * item.quantity;
        }, 0) * (1 + taxRate);
      }
      ```
    expected_behaviors:
      - "Adds type annotation for the `items` parameter (array of objects with price and quantity)"
      - "Adds type annotation for the `taxRate` parameter (number)"
      - "Adds return type annotation"
    judge_criteria:
      - "TypeScript compiles with strict mode and no errors"
      - "Correctly infers or declares item shape with price: number and quantity: number"

  - id: ds-03
    name: "JavaScript async/await conversion"
    description: "Convert Promise .then() chain to async/await syntax"
    tags: [javascript, async]
    prompt: |
      Convert this Promise chain to use async/await:

      ```javascript
      function fetchUserData(userId) {
        return fetch(`/api/users/${userId}`)
          .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
          })
          .then(data => {
            return fetch(`/api/users/${data.teamId}/members`);
          })
          .then(res => res.json())
          .catch(err => console.error('Failed:', err));
      }
      ```
    expected_behaviors:
      - "Uses async/await instead of .then() chaining"
      - "Preserves the error handling with try/catch"
      - "Retains the same logic and API call structure"
    judge_criteria:
      - "Uses async keyword on function declaration"
      - "Uses await for each fetch call"
      - "Uses try/catch instead of .catch()"

  - id: ds-04
    name: "SQL injection prevention"
    description: "Fix a SQL query vulnerable to injection by using parameterized queries"
    tags: [python, sql, security]
    prompt: |
      Fix the SQL injection vulnerability in this Python function. Use parameterized queries.

      ```python
      import sqlite3

      def get_user_by_email(email):
          conn = sqlite3.connect('users.db')
          cursor = conn.cursor()
          query = f"SELECT id, name, email FROM users WHERE email = '{email}'"
          cursor.execute(query)
          return cursor.fetchone()
      ```
    expected_behaviors:
      - "Replaces f-string interpolation with parameterized query (?)"
      - "Passes email as a parameter to execute()"
    judge_criteria:
      - "No string concatenation or f-string in SQL query"
      - "Uses ? placeholder and passes email as execute() argument"
      - "Query logic and return value remain unchanged"

  - id: ds-05
    name: "Python import reorganization"
    description: "Sort and reorganize imports according to PEP8 conventions"
    tags: [python, style]
    prompt: |
      Reorganize these Python imports following PEP8 convention (standard library, third-party, local):

      ```python
      import json
      from datetime import datetime
      import os
      import sys
      import requests
      from flask import Flask, request
      from myproject.utils.helpers import format_date
      from myproject.models import User
      import numpy as np
      ```
    expected_behaviors:
      - "Groups imports into standard library, third-party, and local blocks"
      - "Sorts alphabetically within each group"
      - "Separates groups with blank lines"
    judge_criteria:
      - "Standard library imports come first (json, datetime, os, sys)"
      - "Third-party imports next (flask, numpy, requests)"
      - "Local imports last (myproject)"
      - "Groups separated by blank lines"

  - id: ds-06
    name: "Go nil check"
    description: "Add nil check before dereferencing a pointer in Go"
    tags: [go, safety]
    prompt: |
      Add a nil check before dereferencing the pointer in this Go function:

      ```go
      type Config struct {
        Port int
        Timeout time.Duration
      }

      func StartServer(cfg *Config) error {
        port := cfg.Port
        timeout := cfg.Timeout
        listener, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
        if err != nil {
          return err
        }
        return http.Serve(listener, nil)
      }
      ```
    expected_behaviors:
      - "Adds nil check for cfg before accessing its fields"
      - "Returns an error if cfg is nil"
    judge_criteria:
      - "Checks if cfg == nil before dereferencing"
      - "Returns an error (not panic) when cfg is nil"
      - "Original logic preserved when cfg is non-nil"

  - id: ds-07
    name: "Go error handling"
    description: "Handle an ignored error return value in Go"
    tags: [go, error-handling]
    prompt: |
      Fix the ignored error in this Go function:

      ```go
      import (
        "io"
        "os"
      )

      func CopyFile(src, dst string) error {
        source, err := os.Open(src)
        if err != nil {
          return err
        }
        defer source.Close()

        destination, err := os.Create(dst)
        if err != nil {
          return err
        }
        defer destination.Close()

        io.Copy(destination, source)
        return nil
      }
      ```
    expected_behaviors:
      - "Captures the error return from io.Copy"
      - "Checks the error and returns it if non-nil"
      - "Preserves deferred Close calls"
    judge_criteria:
      - "io.Copy error is assigned to a variable"
      - "Error is checked and returned"
      - "Close is still deferred correctly"

  - id: ds-08
    name: "React stale closure"
    description: "Fix a stale closure bug in React's setInterval with useState"
    tags: [react, javascript, hooks]
    prompt: |
      Fix the stale closure bug in this React component. The counter should increment every second.

      ```jsx
      function Counter() {
        const [count, setCount] = React.useState(0);

        React.useEffect(() => {
          const id = setInterval(() => {
            setCount(count + 1);
          }, 1000);
          return () => clearInterval(id);
        }, []);

        return <div>{count}</div>;
      }
      ```
    expected_behaviors:
      - "Uses functional update form of setCount (prev => prev + 1)"
      - "Keeps the empty dependency array"
      - "Preserves the cleanup function"
    judge_criteria:
      - "setCount receives a function instead of a value"
      - "Count increments correctly without stale values"
      - "No unnecessary re-creations of the interval"

  - id: ds-09
    name: "Dockerfile optimization"
    description: "Improve Dockerfile layer caching for a Node.js app"
    tags: [docker, devops]
    prompt: |
      Optimize this Dockerfile for better layer caching. Package.json should change less often than source code.

      ```dockerfile
      FROM node:20-alpine
      WORKDIR /app
      COPY . .
      RUN npm install
      RUN npm run build
      EXPOSE 3000
      CMD ["npm", "start"]
      ```
    expected_behaviors:
      - "Copies package.json and package-lock.json before other files"
      - "Runs npm install before copying source code"
      - "Keeps the same base image, expose, and CMD"
    judge_criteria:
      - "COPY package*.json ./ comes before COPY . ."
      - "RUN npm install comes before COPY . ."
      - "Build and runtime steps are preserved"

  - id: ds-10
    name: "Regex validation"
    description: "Write an email validation regex in Python"
    tags: [python, regex]
    prompt: |
      Write a function that validates email addresses using regex. The regex should handle typical email formats:

      ```python
      import re

      def is_valid_email(email: str) -> bool:
          # Write regex pattern here
          pass
      ```
    expected_behaviors:
      - "Defines a regex pattern for basic email validation"
      - "Uses re.match or re.fullmatch"
      - "Returns True for valid emails and False for invalid"
    judge_criteria:
      - "Matches user@example.com, a.b@domain.co, name+tag@company.org"
      - "Rejects missing @, missing domain, spaces in address"
      - "Uses re.match or re.fullmatch (not re.search without anchors)"
---
