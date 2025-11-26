import type { Config } from "tailwindcss";

// esta es la configuracion de los estilos de la pagina
const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0D0D0F", // fondo de la pagina, negro oscuro 
        surface: "#1A1A1D", // fondo de la barra de navegacion, gris claro
        primary: "#7F5AF0", // color primario, rosa
        secondary: "#2CB67D", // color secundario, entre azul y morado
        warning: "#FFB800", // color de advertencia, amarillo
        danger: "#EF4565", // color de error, rojo casi rosa 
        text: {
          primary: "#EDEDED", // texto primario, gris claro
          secondary: "#AFAFAF", // texto secundario, gris medio
        },
        border: "#2A2A2E", // color de borde, gris medio fuerte 
      }
    }
  },
  plugins: [],
};

export default config;
