import docker

def run_scraper_in_docker(url):
    """
    Spins up a Docker container to run the scraper module and returns the output.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The output from the scraper module.
    """
    client = docker.from_env()

    try:
        # Build the Docker image
        client.images.build(path=".", tag="scraper_image")

        # Run the Docker container
        container = client.containers.run(
            image="scraper_image",
            command=["python", "scraper_module.py", url],
            detach=True,
            stdout=True,
            stderr=True
        )

        # Wait for the container to finish and get the logs
        container.wait()
        logs = container.logs().decode("utf-8")

        # Clean up the container
        container.remove()

        return logs
    except Exception as e:
        return f"An error occurred while running the scraper in Docker: {e}"

if __name__ == "__main__":
    test_url = "https://www.getintopc.com"
    print(run_scraper_in_docker(test_url))
