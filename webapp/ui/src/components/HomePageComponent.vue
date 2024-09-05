<template>
  <div class="homepage-container">
    <header>
      <img src="/logo.png" alt="Advisor AI Logo">
      <div class="auth-links">
        <el-button type="primary" @click="$router.push('/user/login')">Login</el-button>
        <el-button type="success" @click="$router.push('/user/waitlist')">Join Waitlist</el-button>
        <el-button type="info" @click="$router.push('/membership/pricing')">Pricing</el-button>
      </div>
    </header>
    
    <div class="container">
      <div class="section">
        <div>
          <el-row class="center-content">
            <el-col :span="24">
              <h1 class="homepage-title">
                talkto.app/<VueTyper
                  :text="dynamicWords"
                  :repeat="Infinity"
                  initial-action="typing"
                  :start-delay="200"
                  :type-delay="100"
                  :erase-delay="1000"
                  :erase-speed="100"
                />
              </h1>
            </el-col>
          </el-row>
        </div>
        <div class="subtitle-container">
          <el-row class="center-content">
            <el-col :span="24">
              <div class="homepage-subtitle">
                <!-- <p style="line-height: 24px;">TalkTo is a platform that allows you to connect with the people you want to talk to.</p> -->
                <el-input
                  v-model="userInput"
                  @keyup.enter="handleEnterKey"
                  placeholder="Who do you want to talk to?"
                  class="user-input1"
                />
                <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      dynamicWords: ["celebrity", "influencer", "coach", "chhota-bheem", "doremon"],
      userInput: "",
      errorMessage: ""
    };
  },
  methods: {
    handleEnterKey() {
      // Check if the input contains spaces
      if (/\s/.test(this.userInput)) {
        this.errorMessage = "Input should not contain spaces.";
      } else if (this.userInput.trim() === "") {
        this.errorMessage = "Input cannot be empty.";
      } else {
        // No spaces, proceed to redirect
        this.errorMessage = "";
        this.$router.push(`/${this.userInput}`);
      }
    }
  }
};
</script>

<style>
.homepage-container {
  /* display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center; */
  height: 100vh;
  background-color: #f5f5f5;
  display: block;
  overflow: hidden;
}
.container {
    max-width: 1200px;
    margin: 2em auto;
    padding: 2em;
    background: #fff;
    box-shadow: 0 2px 4px #0000001a;
    border-radius: 8px
}
.homepage-title {
    line-height: 30px;
    font-weight: bold;
    margin: 0 auto 20px auto;
    height: 60px;
    max-width: 475px;
    text-align: left;
}

.homepage-subtitle {
  font-size: 1.2em;
  color: #555;
  text-align: center;
}

.user-input {
  padding: 10px;
  font-size: 1em;
  margin-top: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.error {
  color: red;
  margin-top: 10px;
}

.center-content {
  text-align: center;
}
header img {
    max-height: 50px;
}

header .auth-links {
    float: right;
}

header {padding: 10px;}
</style>
