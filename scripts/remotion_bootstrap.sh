#!/usr/bin/env bash
set -euo pipefail
TARGET_DIR=${1:?usage: remotion_bootstrap.sh <target-dir>}
mkdir -p "$TARGET_DIR/src" "$TARGET_DIR/public"
cd "$TARGET_DIR"
if [ ! -f package.json ]; then
  npm init -y >/dev/null 2>&1
fi
npm install remotion react react-dom >/dev/null 2>&1
cat > src/Root.tsx <<'EOF'
import {Composition} from 'remotion';
import {VideoComposition} from './VideoComposition';
import config from '../video.config.json';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="VideoComposition"
      component={VideoComposition}
      durationInFrames={config.durationInFrames}
      fps={config.fps}
      width={config.width}
      height={config.height}
      defaultProps={{config}}
    />
  );
};
EOF
cat > src/VideoComposition.tsx <<'EOF'
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, Video} from 'remotion';

export const VideoComposition: React.FC<{config: any}> = ({config}) => {
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      {config.scenes.map((scene: any, i: number) => {
        const from = scene.from ?? 0;
        const durationInFrames = scene.durationInFrames;
        return (
          <Sequence key={i} from={from} durationInFrames={durationInFrames}>
            {scene.type === 'video' ? (
              <Video src={scene.src} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
            ) : (
              <Img src={scene.src} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
            )}
          </Sequence>
        );
      })}
      {config.voiceover ? <Audio src={config.voiceover} /> : null}
      {config.music ? <Audio src={config.music} volume={config.musicVolume ?? 0.25} /> : null}
    </AbsoluteFill>
  );
};
EOF
cat > remotion.config.ts <<'EOF'
import {Config} from 'remotion';
Config.setVideoImageFormat('jpeg');
EOF
cat > video.config.json <<'EOF'
{
  "fps": 30,
  "width": 1080,
  "height": 1920,
  "durationInFrames": 150,
  "voiceover": null,
  "music": null,
  "musicVolume": 0.2,
  "scenes": []
}
EOF
printf 'Bootstrapped Remotion project in %s\n' "$TARGET_DIR"
