docker build -t accreditation_disk_bot_v2 .
docker run --env-file .env -d accreditation_disk_bot_v2