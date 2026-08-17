docker compose up -d postgres kafka migrate consumer
docker compose --profile producer run --rm producer python -m services.producer.main --event-count 25 --rate-per-second 20 --seed 42
Start-Sleep -Seconds 5
docker compose exec postgres psql -U platform -d ecommerce -c "select event_type, count(*) from processed_events group by event_type order by event_type;"
