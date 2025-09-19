// Ejemplo básico de layout tipo tmux en C++ con ncurses
// Compila con: g++ -o paneles paneles.cpp -lncurses
#include <ncurses.h>
#include <string>
#include <vector>
#include <cstdlib>

int main() {
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    // Deshabilitar completamente el soporte de ratón
    mousemask(0, NULL);
    // Filtrar códigos de teclas especiales (rueda/clicks)

    int rows, cols;
    getmaxyx(stdscr, rows, cols);

    int left_w = cols * 0.6; // Panel izquierdo más ancho
    int right_w = cols - left_w;
    int right_h1 = rows * 0.3; // Panel derecho superior más estrecho
    int right_h2 = rows - right_h1;

    // Crear ventanas
    WINDOW* left = newwin(rows, left_w, 0, 0);
    WINDOW* right_top = newwin(right_h1, right_w, 0, left_w);
    WINDOW* right_bottom = newwin(right_h2, right_w, right_h1, left_w);

    // Dibujar bordes
    box(left, 0, 0);
    box(right_top, 0, 0);
    box(right_bottom, 0, 0);

    // Etiquetas
    mvwprintw(left, 0, 2, " Panel Izquierdo (Prompt) ");
    mvwprintw(right_top, 0, 2, " Panel Derecho Superior ");
    mvwprintw(right_bottom, 0, 2, " Panel Derecho Inferior ");

    wrefresh(left);
    wrefresh(right_top);
    wrefresh(right_bottom);

    // Versión mínima: solo historial y scroll con PageUp/PageDown
    std::vector<std::string> history;
    int scroll_offset = 0;
    int max_lines = rows - 3;
    int ch;
    // Rellenar historial de prueba
    for (int i = 0; i < 50; ++i) history.push_back("Línea de ejemplo " + std::to_string(i+1));
    auto redraw = [&]() {
        werase(left);
        box(left, 0, 0);
        mvwprintw(left, 0, 2, " Panel Izquierdo (Scroll demo) ");
        int start = std::max(0, (int)history.size() - max_lines - scroll_offset);
        int end = std::min((int)history.size(), start + max_lines);
        int line = 1;
        for (int i = start; i < end; ++i) {
            mvwprintw(left, line++, 2, "%s", history[i].c_str());
        }
        wrefresh(left);
    };
    redraw();
    while ((ch = wgetch(left)) != KEY_F(10)) { // F10 para salir
        if (ch == KEY_PPAGE) { // PageUp
            if ((int)history.size() > max_lines && scroll_offset < (int)history.size() - max_lines) {
                scroll_offset++;
                redraw();
            }
            continue;
        }
        if (ch == KEY_NPAGE) { // PageDown
            if (scroll_offset > 0) {
                scroll_offset--;
                redraw();
            }
            continue;
        }
    }

    delwin(left);
    delwin(right_top);
    delwin(right_bottom);
    endwin();
    return 0;
}
