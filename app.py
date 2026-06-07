"""Root entry point for Vintage Vinyl Store."""

from vinyl_store.app import app, kit

if __name__ == "__main__":
    kit.run(host="0.0.0.0", port=5000, debug=True)
