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
```
ProyectoResumenSesionIA
├─ .git
│  ├─ config
│  ├─ description
│  ├─ HEAD
│  ├─ hooks
│  │  ├─ applypatch-msg.sample
│  │  ├─ commit-msg.sample
│  │  ├─ fsmonitor-watchman.sample
│  │  ├─ post-update.sample
│  │  ├─ pre-applypatch.sample
│  │  ├─ pre-commit.sample
│  │  ├─ pre-merge-commit.sample
│  │  ├─ pre-push.sample
│  │  ├─ pre-rebase.sample
│  │  ├─ pre-receive.sample
│  │  ├─ prepare-commit-msg.sample
│  │  ├─ push-to-checkout.sample
│  │  ├─ sendemail-validate.sample
│  │  └─ update.sample
│  ├─ index
│  ├─ info
│  │  └─ exclude
│  ├─ logs
│  │  ├─ HEAD
│  │  └─ refs
│  │     ├─ heads
│  │     │  └─ master
│  │     └─ remotes
│  │        └─ origin
│  │           └─ HEAD
│  ├─ objects
│  │  ├─ info
│  │  └─ pack
│  │     ├─ pack-df4179407865371eb87ddb16f0bbb262312384bc.idx
│  │     ├─ pack-df4179407865371eb87ddb16f0bbb262312384bc.pack
│  │     └─ pack-df4179407865371eb87ddb16f0bbb262312384bc.rev
│  ├─ packed-refs
│  └─ refs
│     ├─ heads
│     │  └─ master
│     ├─ remotes
│     │  └─ origin
│     │     └─ HEAD
│     └─ tags
├─ .gitignore
├─ .VSCodeCounter
│  ├─ 2024-11-05_19-24-39
│  │  ├─ details.md
│  │  ├─ diff-details.md
│  │  ├─ diff.csv
│  │  ├─ diff.md
│  │  ├─ diff.txt
│  │  ├─ results.csv
│  │  ├─ results.json
│  │  ├─ results.md
│  │  └─ results.txt
│  └─ 2024-11-18_09-48-27
│     ├─ details.md
│     ├─ diff-details.md
│     ├─ diff.csv
│     ├─ diff.md
│     ├─ diff.txt
│     ├─ results.csv
│     ├─ results.json
│     ├─ results.md
│     └─ results.txt
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
   ├─ transcription
   │  ├─ transcribe_audio.py
   │  └─ __init__.py
   └─ __init__.py

```
```
ProyectoResumenSesionIA
├─ .git
│  ├─ config
│  ├─ description
│  ├─ HEAD
│  ├─ hooks
│  │  ├─ applypatch-msg.sample
│  │  ├─ commit-msg.sample
│  │  ├─ fsmonitor-watchman.sample
│  │  ├─ post-update.sample
│  │  ├─ pre-applypatch.sample
│  │  ├─ pre-commit.sample
│  │  ├─ pre-merge-commit.sample
│  │  ├─ pre-push.sample
│  │  ├─ pre-rebase.sample
│  │  ├─ pre-receive.sample
│  │  ├─ prepare-commit-msg.sample
│  │  ├─ push-to-checkout.sample
│  │  ├─ sendemail-validate.sample
│  │  └─ update.sample
│  ├─ index
│  ├─ info
│  │  └─ exclude
│  ├─ logs
│  │  ├─ HEAD
│  │  └─ refs
│  │     ├─ heads
│  │     │  └─ master
│  │     └─ remotes
│  │        └─ origin
│  │           └─ HEAD
│  ├─ objects
│  │  ├─ info
│  │  └─ pack
│  │     ├─ pack-df4179407865371eb87ddb16f0bbb262312384bc.idx
│  │     ├─ pack-df4179407865371eb87ddb16f0bbb262312384bc.pack
│  │     └─ pack-df4179407865371eb87ddb16f0bbb262312384bc.rev
│  ├─ packed-refs
│  └─ refs
│     ├─ heads
│     │  └─ master
│     ├─ remotes
│     │  └─ origin
│     │     └─ HEAD
│     └─ tags
├─ .gitignore
├─ .VSCodeCounter
│  ├─ 2024-11-05_19-24-39
│  │  ├─ details.md
│  │  ├─ diff-details.md
│  │  ├─ diff.csv
│  │  ├─ diff.md
│  │  ├─ diff.txt
│  │  ├─ results.csv
│  │  ├─ results.json
│  │  ├─ results.md
│  │  └─ results.txt
│  └─ 2024-11-18_09-48-27
│     ├─ details.md
│     ├─ diff-details.md
│     ├─ diff.csv
│     ├─ diff.md
│     ├─ diff.txt
│     ├─ results.csv
│     ├─ results.json
│     ├─ results.md
│     └─ results.txt
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
   ├─ transcription
   │  ├─ transcribe_audio.py
   │  └─ __init__.py
   └─ __init__.py

```