from agno.memory.strategies.types import MemoryOptimizationStrategyType

from app.memory import memory_manager


def optimize_user_memory(user_id: str = "Friend") -> None:
    """
    Summarizes and optimizes user memories to reduce token usage and improve relevance.
    Best Practice: Run this periodically or after long sessions.
    """
    print(f"Optimizing memories for user: {user_id}...")

    try:
        optimized = memory_manager.optimize_memories(
            user_id=user_id,
            strategy=MemoryOptimizationStrategyType.SUMMARIZE,
            apply=True,
        )
        print(f"✅ Success! Optimized {len(optimized)} memories.")
    except Exception as e:
        print(f"❌ Error optimizing memories: {e}")

if __name__ == "__main__":
    optimize_user_memory()
