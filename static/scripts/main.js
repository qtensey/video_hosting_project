 const profileBtn = document.getElementById('profileButton');
    const profileMenu = document.getElementById('profileMenu');

    profileBtn.addEventListener('click', () => {
      profileMenu.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
        profileMenu.classList.remove('show');
      }
    });