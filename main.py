import json

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import google, noise_cancellation

# from livekit.plugins import (cartesia, deepgram, google, noise_cancellation, silero)
# from livekit.plugins.turn_detector.multilingual import MultilingualModel
# from livekit.plugins.turn_detector.english import EnglishModel

load_dotenv()


class Assistant(Agent):
    def __init__(self, instructions: str = "") -> None:
        super().__init__(instructions=instructions)


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    # Parse metadata instructions
    metadata = json.loads(ctx.room.metadata or "{}")
    instructions = metadata.get("instructions", "You are a helpful assistant.")

    agent = Assistant(instructions=instructions)

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            # model="gemini-2.0-flash-exp",
            model="gemini-2.0-flash-live-001",
            voice="Kore",  # "Puck",
            temperature=0.3,  # 0.8,
            instructions=instructions,
        ),
    )

    # session = AgentSession(
    #     stt=deepgram.STT(language="en"),
    #     # llm=google.LLM(
    #     #     model="gemini-2.0-flash-exp",
    #     #     temperature=0.8,
    #     # ),
    #     llm=google.beta.realtime.RealtimeModel(
    #         model="gemini-2.0-flash-exp",
    #         voice="Puck",
    #         # temparature=0.8,
    #     ),
    #     tts=cartesia.TTS(),
    #     vad=silero.VAD.load(),
    #     turn_detection=MultilingualModel(local_files_only=False),
    #     # turn_detection=EnglishModel(),
    # )
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user as an interviewee and ask questions."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
