# Building GroqStockScriptAI: My First Hands-On AI Engineering Project

## What I set out to build

After 18 years writing software, I wanted to actually build something with the current AI stack — not read about it, build it. The idea: pick a stock, get an AI-generated market summary grounded in real, live data. Simple on paper. The value wasn't in the idea being novel — it was in forcing myself through every real decision an AI-powered product actually requires: what data to trust, how to talk to an LLM safely, how to ship it somewhere real people could use it.

## Step 1: Starting with a UI skeleton, not the AI

Before touching yfinance or any LLM, I built the Gradio interface with a dummy function — a textbox, a button, an output box that just echoed back whatever was typed in. No real logic at all.

This mattered more than it sounds. Proving the wiring works end-to-end — input reaches a function, a function's output reaches the screen — before adding any real complexity meant that when something broke later, I knew it wasn't the UI. Cheap insurance, paid early.

## Step 2: Fetching real data, and choosing not to over-build

`yfinance` gives you live price, volume, and P/E data for a stock ticker. The obvious "proper" version of this feature would accept any ticker a user types, validate it, correct common mistakes (like adding `.NS` for Indian exchanges automatically), and handle every malformed input gracefully.

I didn't build that. I hardcoded a list of 9 known-good tickers (5 NSE, 4 US) and used a dropdown instead of free text. That one decision deleted an entire category of edge cases — invalid tickers, exchange-suffix guessing, fuzzy input handling — for a version whose actual goal was proving the data pipeline worked, not building a general-purpose stock search engine. Knowing what *not* to build yet turned out to be the harder, more valuable skill than any of the code itself.

## Step 3: Learning that LLMs will confidently lie if you let them

The first version of my prompt just said "analyze this stock's data." The model happily invented specific reasons for price moves — a fabricated earnings miss, a made-up news event — because I'd asked it to explain "why," and it had no way to know it didn't actually have that information. It answered anyway, fluently and wrongly.

The fix was one paragraph in the system prompt: instruct the model to reason only from the numeric data it was actually given (price, volume, P/E, trend), and explicitly forbid it from asserting specific real-world causes it wasn't given data for. The output quality changed immediately — instead of inventing a cause, it started describing patterns ("this shows a declining trend, potentially reflecting reduced investor confidence") without claiming to know the specific reason.

This is the core lesson of working with LLMs in a real product: **the model doesn't know what it doesn't know, and it won't tell you that unprompted.** You have to build that boundary yourself, the same way you'd validate any other untrusted input in a normal application.

## Step 4: Provider abstraction — a small decision with a real payoff

I used Groq to run Llama 3.3 70B, but instead of using Groq's own Python package, I used the standard `openai` SDK pointed at Groq's OpenAI-compatible endpoint. Functionally identical output, but now the LLM provider is swappable by changing two config values — an API key and a base URL — not application code. In a market where LLM providers change pricing and availability quickly, that's not a hypothetical concern; it's exactly what happened one phase later with hosting.

## Step 5: Environment variables and the discipline of keeping secrets out of code

`GROQ_API_KEY` never appears anywhere in the codebase — it's read from an environment variable, loaded locally via a `.env` file that's explicitly excluded from git, and injected as a real environment variable in production. A `.env.example` file documents which variable is required without exposing a real value, so anyone cloning the repo knows what to configure.

This is unglamorous, but it's the difference between a project that's safe to make public and one that leaks a credential the first time someone clones it.

## Step 6: A platform pivot I didn't choose

My original plan — and the plan documented in my requirements doc — was to deploy on Hugging Face Spaces, which was free for Gradio apps. Partway through the project, Hugging Face moved Gradio-SDK Spaces behind a paid tier; only static, non-Python Spaces stayed free. No amount of local testing would have caught that — it was a business decision on their end, not a bug on mine.

I pivoted to Render instead, which meant learning something local development never teaches: cloud hosts assign your app's listening port *dynamically*, via an environment variable, at runtime. My app needed two small changes — bind to `0.0.0.0` instead of `localhost`, and read the port from `os.environ.get("PORT", ...)` instead of hardcoding it — before it would even start on Render's infrastructure.

## Step 7: A debugging detour that had nothing to do with AI

Pushing to GitHub failed with a permissions error — because I have two GitHub accounts on the same machine, and Windows had cached the wrong one's credentials. Fixing it meant clearing the cached credential via Windows Credential Manager and re-authenticating as the right account. Not an AI problem, not even really a coding problem — just real infrastructure friction that doesn't show up in tutorials, and that any engineer eventually has to debug regardless of what they're building.

## What I'd do differently next time

I'd verify a hosting platform's actual pricing/limits *before* writing deployment-specific documentation around it, rather than discovering the change mid-project. It didn't cost much time here, but it's the kind of assumption worth checking earlier.

## Key takeaways (for the LinkedIn/article version)

- Scoping down aggressively — a hardcoded stock list instead of full ticker search — was a deliberate engineering decision, not a shortcut. Knowing what not to build yet is still the hardest skill, 18 years in or on day one.
- An LLM without explicit constraints will confidently fabricate plausible-sounding but false explanations. Building that guardrail is not optional if the output needs to be trustworthy.
- Provider abstraction (using an OpenAI-compatible client instead of a vendor-specific SDK) paid for itself almost immediately when a hosting platform's pricing changed mid-project.
- Real production friction — platform pivots, credential conflicts, dynamic port binding — is where the actual learning happens, far more than the AI integration itself.
