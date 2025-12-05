"""
test_llama.py - Basic testing script for llama.cpp deployment
"""

import requests
import time
import json
import sys
from typing import Dict, List
import statistics

class LlamaClient:
    def __init__(self, base_url: str = "http://localhost:80"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check if the server is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def chat(self, message: str, max_tokens: int = 100) -> Dict:
        """Send a chat message using the chat completions endpoint"""
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        start_time = time.time()
        response = self.session.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        latency = time.time() - start_time
        
        response.raise_for_status()
        result = response.json()
        result['latency'] = latency
        
        return result
    
    def generate(self, prompt: str, max_tokens: int = 100) -> Dict:
        """Generate text from prompt"""
        payload = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stream": False,
            "stop": ["<|im_end|>", "</s>", "<|endoftext|>"]
        }
        
        start_time = time.time()
        response = self.session.post(
            f"{self.base_url}/completion",
            json=payload,
            timeout=30
        )
        latency = time.time() - start_time
        
        response.raise_for_status()
        result = response.json()
        result['latency'] = latency
        
        return result
    
    def benchmark(self, prompts: List[str], iterations: int = 5) -> Dict:
        """Run benchmark tests"""
        results = {
            'latencies': [],
            'tokens_per_second': [],
            'successes': 0,
            'failures': 0
        }
        
        total_tests = len(prompts) * iterations
        current_test = 0
        
        for iteration in range(iterations):
            for prompt in prompts:
                current_test += 1
                print(f"Running test {current_test}/{total_tests}...", end='\r')
                
                try:
                    result = self.generate(prompt)
                    results['latencies'].append(result['latency'])
                    
                    # Calculate tokens per second if available
                    if 'timings' in result:
                        tokens = result['timings'].get('predicted_n', 0)
                        time_s = result['timings'].get('predicted_ms', 0) / 1000
                        if time_s > 0:
                            results['tokens_per_second'].append(tokens / time_s)
                    
                    results['successes'] += 1
                except Exception as e:
                    print(f"\nTest failed: {e}")
                    results['failures'] += 1
        
        print()  # New line after progress
        return results


def print_results(results: Dict):
    """Print formatted benchmark results"""
    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    
    if results['latencies']:
        latencies = results['latencies']
        print(f"\nLatency Statistics:")
        print(f"  Average: {statistics.mean(latencies):.3f}s")
        print(f"  Median:  {statistics.median(latencies):.3f}s")
        print(f"  P95:     {sorted(latencies)[int(len(latencies)*0.95)]:.3f}s")
        print(f"  P99:     {sorted(latencies)[int(len(latencies)*0.99)]:.3f}s")
        print(f"  Min:     {min(latencies):.3f}s")
        print(f"  Max:     {max(latencies):.3f}s")
    
    if results['tokens_per_second']:
        tps = results['tokens_per_second']
        print(f"\nTokens Per Second:")
        print(f"  Average: {statistics.mean(tps):.2f}")
        print(f"  Median:  {statistics.median(tps):.2f}")
    
    print(f"\nTest Summary:")
    print(f"  Successes: {results['successes']}")
    print(f"  Failures:  {results['failures']}")
    print(f"  Success Rate: {results['successes']/(results['successes']+results['failures'])*100:.1f}%")
    print("="*50)


def main():
    # Test prompts
    test_prompts = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms.",
        "Write a haiku about autumn.",
        "What are the benefits of exercise?",
        "Tell me about the solar system."
    ]
    
    print("Personal GPT - llama.cpp Test Suite")
    print("=" * 50)
    
    # Initialize client
    client = LlamaClient()
    
    # Health check
    print("\n1. Health Check...")
    if not client.health_check():
        print("Server is not healthy. Please check deployment.")
        sys.exit(1)
    print("Server is healthy")
    
    # Single test
    print("\n2. Single Generation Test...")
    try:
        result = client.generate("Hello, how are you?", max_tokens=50)
        print(f"Generation successful")
        print(f"   Latency: {result['latency']:.3f}s")
        print(f"   Response: {result.get('content', 'N/A')[:100]}...")
    except Exception as e:
        print(f"Generation failed: {e}")
        sys.exit(1)
    
    # Benchmark
    print("\n3. Running Benchmark...")
    print("This may take a few minutes...")
    results = client.benchmark(test_prompts, iterations=3)
    print_results(results)
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"benchmark_results_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()