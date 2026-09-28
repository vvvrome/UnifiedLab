"""Launch the preserved PhysicLab Flask app on port 5001."""
import sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / "PhysicLab"))
import app as physiclab_app  # noqa: E402

if __name__ == "__main__":
    physiclab_app.app.run(host="0.0.0.0", port=5001, debug=False)
