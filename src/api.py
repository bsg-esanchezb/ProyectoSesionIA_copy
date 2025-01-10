from fastapi import FastAPI
from src.routers import video, audio, transcription, summary, study_guide, podcast, concept_map, big_workflow

app = FastAPI(
    title="Video and Audio Processing API",
    version="1.0.0",
    description="API for video processing, transcription, summarization, study guides, podcasts, and concept maps"
)

app.include_router(video.router, prefix="/api/v1/videos", tags=["Videos"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio"])
app.include_router(transcription.router, prefix="/api/v1/transcription", tags=["Transcription"])
app.include_router(summary.router, prefix="/api/v1/summary", tags=["Summary"])
app.include_router(study_guide.router, prefix="/api/v1/study-guide", tags=["Study Guide"])
app.include_router(podcast.router, prefix="/api/v1/podcast", tags=["Podcast"])
app.include_router(concept_map.router, prefix="/api/v1/concept-map", tags=["Concept Map"])
app.include_router(big_workflow.router, prefix="/api/v1/workflow", tags=["Workflow"])
