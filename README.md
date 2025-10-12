### What is a readme file?


uv pip install -e .


I can't generate the SSH key for you, but I can walk you through it.

  1. Generate an SSH key on your local machine

  First, open a terminal on your local machine and run:

   1 ssh-keygen -t ed25519 -C "jdmasciano2@gmail.com"

  Press Enter to accept the default file location and, if you wish, enter a passphrase.

  2. Add the SSH key to your GitHub account

   1. Copy the public key. In your local terminal, run:

   1     cat ~/.ssh/id_ed25519.pub

   2. Add the key to GitHub. Go to your GitHub settings, find "SSH and GPG keys," and click "New SSH key." Title
      it (e.g., "My Local VS Code") and paste the copied key.

  3. Repeat for your IDX environment

  Follow the same steps in your IDX terminal to generate and add a new SSH key to your GitHub account, giving
  it a unique title like "IDX Environment."

  4. Configure VS Code to use SSH for Git

   1. Get the SSH URL. On your GitHub repo page, click "Code" and copy the SSH URL.

   2. Update the remote URL. In both your local and IDX terminals, run:

   1     git remote set-url origin git@github.com:surfiniaburger/vigilant-journey.git

  After this, you should be able to use Git in both environments without a password. Let me know if you have
  questions.
