├─ data
│  ├─ input
│  │  └─ videos
│  ├─ output
│  │  ├─ concept_map
│  │  ├─ podcast
│  │  ├─ study_guides
│  │  ├─ transcriptions
│  │  └─ videos
│  └─ temp
│     ├─ audios
│     ├─ chunks
│     │  └─ summary
│     ├─ podcast
│     ├─ podcast_text
│     └─ summary
├─ README.md
├─ requirements.txt
└─ src
   ├─ api.py
   ├─ audio_extraction
   │  ├─ extract_audio.py
   │  ├─ path
   │  │  └─ to
   │  │     └─ output
   │  └─ __init__.py
   ├─ celery_tasks
   │  ├─ celery.py
   │  ├─ tasks.py
   │  └─ __init__.py
   ├─ config.py
   ├─ database.py
   ├─ download_video
   │  ├─ download_video.py
   │  └─ __init__.py
   ├─ repositories
   │  ├─ procesamiento_repository.py
   │  └─ __init__.py
   ├─ routers
   │  ├─ audio.py
   │  ├─ big_workflow.py
   │  ├─ concept_map.py
   │  ├─ podcast.py
   │  ├─ processing.py
   │  ├─ session.py
   │  ├─ study_guide.py
   │  ├─ summary.py
   │  ├─ transcription.py
   │  ├─ video.py
   │  └─ __init__.py
   ├─ services
   │  ├─ audio_service.py
   │  ├─ big_workflow_service.py
   │  ├─ concept_map_service.py
   │  ├─ podcast_service.py
   │  ├─ study_guide_service.py
   │  ├─ summarization_service.py
   │  ├─ transcription_service.py
   │  └─ video_service.py
   ├─ summarization
   │  ├─ summarization.py
   │  └─ __init__.py
   ├─ test.py
   ├─ text_to_audio
   │  ├─ text_to_audio.py
   │  └─ __init__.py
   ├─ text_to_concept_map
   │  ├─ debug_mermaid.txt
   │  ├─ text_to_concept_map.py
   │  └─ __init__.py
   ├─ text_to_pdf
   │  ├─ text_to_pdf.py
   │  └─ __init__.py
   ├─ text_to_video
   │  ├─ text_to_video.py
   │  ├─ text_to_video_2.py
   │  └─ __init__.py
   └─ transcription
      ├─ transcribe_audio.py
      └─ __init__.py

```