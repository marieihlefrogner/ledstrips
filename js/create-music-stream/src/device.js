const ffmpeg = require('fluent-ffmpeg')
const { spawn } = require('child_process');

// virtual-audio-capturer

module.exports = {

  getDeviceStream(device, log) {
    device = device.split('device:')[1];

    // return spawn('node_modules/ffmpeg-static/bin/win32/x64/ffmpeg.exe -f dshow -i audio="virtual-audio-capturer" pipe:0')

    return ffmpeg('udp://127.0.0.1:8888')
      .inputOptions([
        '-f dshow',
        `-i audio=${device}`,
        'pipe:0',
      ])
      .outputOptions([
        '-f s16le',
        '-acodec pcm_s16le',
        '-vn',
        '-ac 2',
        '-ar 44100',
      ])
      .on('progress', p => log(`Downloaded ${p.targetSize}kb`));
  }
}
