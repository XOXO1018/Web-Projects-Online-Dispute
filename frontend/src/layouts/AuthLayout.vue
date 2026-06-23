<template>
  <div class="auth-layout">
    <div class="auth-background">
      <div class="auth-left">
        <div class="brand-logo-circle">
          <img src="/logo.jpg" alt="智链解纷" class="brand-logo-img" />
        </div>
        <div class="brand">
          <h1>智链解纷</h1>
          <p>中国-东盟跨境商事纠纷在线解决平台</p>
        </div>
        <ul class="features">
          <li>🌏 覆盖东盟10国，多语言支持</li>
          <li>🔒 区块链存证，证据不可篡改</li>
          <li>🎥 在线视频调解，高效解纷</li>
          <li>📄 电子签章，协议即时生效</li>
        </ul>
      </div>
      <div class="auth-right">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #0d1b2a 0%, #162d50 40%, #1b3a5c 60%, #0d1b2a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;

  /* 背景装饰 */
  &::before {
    content: '';
    position: absolute;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(22, 119, 255, 0.08) 0%, transparent 70%);
    top: -200px;
    right: -100px;
    pointer-events: none;
  }

  &::after {
    content: '';
    position: absolute;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(22, 119, 255, 0.05) 0%, transparent 70%);
    bottom: -150px;
    left: -100px;
    pointer-events: none;
  }
}

.auth-background {
  display: flex;
  width: 960px;
  min-height: 620px;
  border-radius: var(--radius-2xl);
  overflow: hidden;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 1;
}

.auth-left {
  flex: 1;
  background: linear-gradient(160deg, #1677ff 0%, #0958d9 50%, #003eb3 100%);
  padding: 48px 44px;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;

  /* 装饰光晕 */
  &::before {
    content: '';
    position: absolute;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    top: -60px;
    right: -80px;
  }

  &::after {
    content: '';
    position: absolute;
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.04);
    bottom: -40px;
    left: -40px;
  }
}

.brand-logo-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  margin-bottom: 32px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;

  .brand-logo-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.brand {
  margin-bottom: 36px;
  text-align: center;
  position: relative;
  z-index: 1;

  h1 {
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 10px;
    letter-spacing: 2px;
  }

  p {
    font-size: 14px;
    opacity: 0.85;
    line-height: 1.7;
  }
}

.features {
  list-style: none;
  position: relative;
  z-index: 1;

  li {
    padding: 12px 0;
    font-size: 14px;
    opacity: 0.9;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    transition: opacity 0.2s;

    &:last-child { border-bottom: none; }
    &:hover { opacity: 1; }
  }
}

.auth-right {
  width: 440px;
  background: #ffffff;
  padding: 56px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

@media (max-width: 768px) {
  .auth-background { flex-direction: column; width: 95vw; min-height: auto; }
  .auth-left { padding: 36px 28px; }
  .auth-right { width: 100%; padding: 36px 28px; }
}
</style>
