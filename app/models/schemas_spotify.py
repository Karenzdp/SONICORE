from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# --- MODELOS GENÉRICOS ---
class SpotifyImage(BaseModel):
    url: str
    height: Optional[int] = None
    width: Optional[int] = None

class SpotifyEntity(BaseModel):
    id: str
    name: str
    uri: str
    external_urls: Dict[str, str]

# --- ARTISTAS ---
class ArtistFull(SpotifyEntity):
    genres: List[str] = []
    images: List[SpotifyImage] = []
    popularity: int = 0

# --- ÁLBUMES ---
class AlbumSimple(SpotifyEntity):
    album_type: str
    total_tracks: int
    images: List[SpotifyImage] = []
    release_date: str

# --- TRACKS ---
class TrackFull(SpotifyEntity):
    album: AlbumSimple
    artists: List[SpotifyEntity]
    duration_ms: int
    popularity: int
    preview_url: Optional[str] = None

# --- PLAYBACK ---
class Device(BaseModel):
    id: Optional[str]
    is_active: bool
    name: str
    type: str
    volume_percent: Optional[int]

class PlaybackState(BaseModel):
    device: Optional[Device]
    is_playing: bool
    item: Optional[TrackFull]
    progress_ms: Optional[int]
    shuffle_state: bool
    repeat_state: str

# --- USER ---
class UserProfile(SpotifyEntity):
    email: Optional[str] = None
    country: Optional[str] = None
    product: Optional[str] = None # premium/free
    followers: Dict[str, Any]
    images: List[SpotifyImage] = []