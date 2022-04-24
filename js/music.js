const Speaker = require('speaker');
const createMusicStream = require('./create-music-stream');
const { MusicBeatDetector, MusicBeatScheduler, MusicGraph } = require('music-beat-detector');
const { Control } = require('magic-home');

if (process.platform === 'win32') {
  require('fluent-ffmpeg').setFfmpegPath('D:\\Downloads\\ffmpeg\\bin\\ffmpeg.exe');
}

let musicSource = process.argv[2];

const musicGraph = new MusicGraph();
const lights = new Control('10.10.123.3', { wait_for_reply: false });

let last_color = 0;
let peak_count = 0;

const musicBeatScheduler = new MusicBeatScheduler(pos => {
  let a = [0, 0, 0];
  
  last_color = (last_color + 1) % 3;

  /* a = a.map((c, i) => {
    if (i == last_color) return 255;
    
    return getRandomInt(0, 100);
  }) */

  //a[last_color] = 255;

  if(peak_count % 2 == 0){
    a = [255, 255, 255]
  }

  lights.setColor(...a);

  peak_count++;

  console.log(`Peak at ${pos}ms. Color: ${a}`);
})

const musicBeatDetector = new MusicBeatDetector({
  plotter: musicGraph.getPlotter(),
  scheduler: musicBeatScheduler.getScheduler(),
  minThreashold: 4000
})

createMusicStream(musicSource)
  .pipe(musicBeatDetector.getAnalyzer())
  .on('peak-detected', (pos, bpm) => {
    //console.log(`peak-detected at ${pos}ms, detected bpm ${bpm}`)
  })
  .on('end', () => {
    //fs.writeFileSync('graph.svg', musicGraph.getSVG())
  })
  .pipe(new Speaker())
  .on('open', () => musicBeatScheduler.start())





