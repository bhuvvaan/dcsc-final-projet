# PPTGaze: PPT Generation Service

This repository includes the complete code to build a software service using Kubernetes that takes a video as input and returns a downloadable PPT presentation. Since the code is containerized using Docker, no additional requirements need to be installed. We recommend using Docker Desktop for running the Kubernetes service.

## How to Use

1. Start the Kubernetes service on Docker Desktop.
2. Run the following command from the root folder to deploy all required components:

    ```bash
    bash deploy-all.sh
    ```

3. Open a browser and navigate to:

    ```
    http://localhost
    ```

4. Log in to the service.
5. Upload an MP4 video file when prompted.
6. After processing, you will receive a prompt to download the generated PPT file.

---

Feel free to reach out for any improvements or comments!

Project demo can be found here [https://www.youtube.com/watch?v=hMuxLK65RBs](url)

Credits:
Bhuvvaan Punukolu &
Prathik Jain
