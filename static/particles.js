  /**
   * yaura pas d'explication sur ce bloc la,cest ma fonction de particules perso
   */
function createParticle() {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    particle.innerText = '❀';
    particle.style.left = Math.random() * window.innerWidth + 'px';
    particle.style.top = '-50px';
    particle.style.fontSize = (Math.random() * 10 + 15) + 'px';
    document.body.appendChild(particle);
    setTimeout(() => particle.remove(), 7000);
}

document.addEventListener('DOMContentLoaded', () => {
    setInterval(createParticle, 1000);
}); 