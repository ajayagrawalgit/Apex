import docker
import os

# Initialize Docker client
client = docker.from_env()

# Define paths
project_dir = os.path.dirname(os.path.abspath(__file__))
dockerfile_path = os.path.join(project_dir, "Dockerfile")

# Create Dockerfile if it doesn't exist
if not os.path.exists(dockerfile_path):
    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(
            """
            FROM python:3.9-slim
            WORKDIR /app
            COPY . /app
            RUN pip install cloudscraper
            CMD ["tail", "-f", "/dev/null"]
            """
        )

# Build Docker image if not already built
image_name = "scraper_image"
if not any(image_name in tag for image in client.images.list() for tag in image.tags):
    client.images.build(path=project_dir, tag=image_name, rm=True)

# Create and start a long-running container
container_name = "scraper_container"
existing_containers = client.containers.list(all=True, filters={"name": container_name})
if existing_containers:
    container = existing_containers[0]
    if container.status != "running":
        container.start()
else:
    container = client.containers.run(
        image=image_name,
        name=container_name,
        detach=True,
        stdin_open=True,
        stdout=True
    )

def run_scraper_in_docker(url):
    """
    Sends a URL to the long-running Docker container and retrieves the scraped content.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The scraped content from the Docker container.
    """
    try:
        # Ensure the container is running
        container.reload()
        if container.status != "running":
            container.start()

        # Send URL to the container's stdin and capture output
        exec_instance = client.api.exec_create(container.id, cmd=f"python -c \"from scraper import scrape_url; print(scrape_url('{url}'))\"")
        output = client.api.exec_start(exec_instance.get("Id"), stream=True)

        # Log output for debugging
        full_output = ""
        for line in output:
            decoded_line = line.decode("utf-8")
            print(f"[DEBUG] Container Output: {decoded_line}")  # Debug log
            full_output += decoded_line

        return full_output.strip()
    except Exception as e:
        print(f"[DEBUG] An error occurred: {e}")  # Debug log
        return f"An error occurred: {e}"
