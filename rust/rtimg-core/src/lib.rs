pub const MAGIC: &[u8; 4] = b"RTI0";
pub const VERSION_MAJOR: u8 = 0;
pub const VERSION_MINOR: u8 = 1;

#[derive(Debug, Clone)]
pub struct Header {
    pub version_major: u8,
    pub version_minor: u8,
    pub profile_id: u8,
    pub flags: u8,
    pub width: u32,
    pub height: u32,
    pub channels: u8,
    pub bit_depth: u8,
    pub color_space: u8,
    pub tile_width: u16,
    pub tile_height: u16,
    pub predictor_id: u8,
    pub entropy_codec_id: u8,
    pub metadata_count: u16,
    pub tile_count: u32,
}

#[derive(thiserror::Error, Debug)]
pub enum RtimgError {
    #[error("invalid magic")]
    InvalidMagic,
    #[error("unsupported version {0}")]
    UnsupportedVersion(u8),
    #[error("unexpected end of file")]
    UnexpectedEof,
    #[error("invalid format: {0}")]
    InvalidFormat(&'static str),
}

pub fn parse_header(bytes: &[u8]) -> Result<Header, RtimgError> {
    if bytes.len() < 32 {
        return Err(RtimgError::UnexpectedEof);
    }
    if &bytes[0..4] != MAGIC {
        return Err(RtimgError::InvalidMagic);
    }
    let version_major = bytes[4];
    let version_minor = bytes[5];
    if version_major != VERSION_MAJOR {
        return Err(RtimgError::UnsupportedVersion(version_major));
    }
    let width = u32::from_le_bytes(bytes[8..12].try_into().unwrap());
    let height = u32::from_le_bytes(bytes[12..16].try_into().unwrap());
    let channels = bytes[16];
    let bit_depth = bytes[17];
    let color_space = bytes[18];
    let tile_width = u16::from_le_bytes(bytes[20..22].try_into().unwrap());
    let tile_height = u16::from_le_bytes(bytes[22..24].try_into().unwrap());
    let predictor_id = bytes[24];
    let entropy_codec_id = bytes[25];
    let metadata_count = u16::from_le_bytes(bytes[26..28].try_into().unwrap());
    let tile_count = u32::from_le_bytes(bytes[28..32].try_into().unwrap());
    if width == 0 || height == 0 {
        return Err(RtimgError::InvalidFormat("width/height cannot be zero"));
    }
    if channels == 0 || bit_depth == 0 {
        return Err(RtimgError::InvalidFormat("channels/bit_depth cannot be zero"));
    }
    Ok(Header {
        version_major,
        version_minor,
        profile_id: bytes[6],
        flags: bytes[7],
        width,
        height,
        channels,
        bit_depth,
        color_space,
        tile_width,
        tile_height,
        predictor_id,
        entropy_codec_id,
        metadata_count,
        tile_count,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_header() {
        let mut header = [0u8; 32];
        header[0..4].copy_from_slice(MAGIC);
        header[4] = VERSION_MAJOR;
        header[5] = VERSION_MINOR;
        header[8..12].copy_from_slice(&16u32.to_le_bytes());
        header[12..16].copy_from_slice(&16u32.to_le_bytes());
        header[16] = 3;
        header[17] = 8;
        header[20..22].copy_from_slice(&8u16.to_le_bytes());
        header[22..24].copy_from_slice(&8u16.to_le_bytes());
        let parsed = parse_header(&header).unwrap();
        assert_eq!(parsed.width, 16);
        assert_eq!(parsed.height, 16);
    }
}
