function setTheme(theme) {
     document.documentElement.className = theme;
     localStorage.setItem('theme', theme);
 }