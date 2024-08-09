<template>
    <el-row justify="center" align="middle" style="height: 100vh;">
        <el-col style="text-align: center;">
            <div class="video-container">
                <video
                    ref="videoPlayer"
                    class="video-js vjs-default-skin"
                    controls
                    width="700"
                >
                    <source :src="videoSrc" type="video/mp4" />
                </video>
            </div>
      </el-col>
    </el-row>
  </template>
  
  <script>
  import videojs from 'video.js';
  import 'video.js/dist/video-js.css';
  
  export default {
    data() {
      return {
        videoSrc: '/videos/demo1-2024-08-08.mp4',
      };
    },
    mounted() {
      this.player = videojs(this.$refs.videoPlayer, {
        playbackRates: [0.5, 1, 1.5, 2],
      });
      this.player.on('ratechange', () => {
        this.playbackRate = this.player.playbackRate();
      });
    },
    watch: {
      playbackRate(newRate) {
        this.player.playbackRate(newRate);
      },
    },
    beforeDestroy() {
      if (this.player) {
        this.player.dispose();
      }
    },
  };
  </script>
  
  <style>
</style>