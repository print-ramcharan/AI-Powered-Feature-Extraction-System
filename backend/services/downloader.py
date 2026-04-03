import httpx
import os

async def download_from_url(url: str, output_path: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            raise Exception(f"Failed to download ZIP from URL: {str(e)}")
