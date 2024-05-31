# Grand Piano Transcription Application

## Overview
This application transcribes grand piano recordings into sheet music and exports the results as a PDF. It processes audio locally for privacy and accessibility.

## Installation

**Note: This application is designed to work only with WSL (Windows Subsystem for Linux) or on a Linux system.**

1. **Clone the repository:**
    ```sh
    git clone https://github.com/mj300405/MP3_to_notes.git
    cd MP3_to_notes
    ```

2. **Set up a virtual environment:**
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Ensure MuseScore is installed and configured.**

5. **Install and configure WSL2:**
    - Follow the official [WSL2 installation guide](https://docs.microsoft.com/en-us/windows/wsl/install) to set up WSL2 on your system.
    - Install a Linux distribution from the Microsoft Store (e.g., Ubuntu).

6. **Install VLC:**
    ```sh
    sudo apt-get update
    sudo apt-get install vlc
    ```

7. **Install and configure an X-server:**
    - Download and install an X-server for Windows, such as [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [Xming](https://sourceforge.net/projects/xming/).
    - Start the X-server before running GUI applications in WSL2.
    - Configure WSL2 to use the X-server by adding the following line to your `.bashrc` or `.zshrc` file:
      ```sh
      export DISPLAY=$(grep -oP '(?<=nameserver\s)[\d.]+' /etc/resolv.conf 2>/dev/null):0
      ```

## Usage

1. **Run the application:**
    ```sh
    python main.py
    ```

2. **Use the GUI to upload MP3 files, transcribe, and manage outputs.**


## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
**Author:** Michał Jagoda  
**Project Link:** [GitHub Repository](https://github.com/mj300405/MP3_to_notes)

## References
- Qiuqiang Kong, Bochen Li, Xuchen Song, Yuan Wan, and Yuxuan Wang. "High-resolution Piano Transcription with Pedals by Regressing Onsets and Offsets Times." arXiv preprint arXiv:2010.01815 (2020). [pdf](https://arxiv.org/pdf/2010.01815.pdf)
