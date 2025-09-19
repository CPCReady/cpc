// Ejemplo básico de layout con FTXUI
#include <ftxui/component/screen_interactive.hpp>
#include <ftxui/component/component.hpp>
#include <ftxui/dom/elements.hpp>
#include <string>
#include <vector>

using namespace ftxui;

int main() {
	auto screen = ScreenInteractive::FitComponent();

	// Panel izquierdo: prompt y salida
	std::vector<std::string> history = {"Bienvenido a FTXUI!"};
	std::string input;

	// Panel derecho superior e inferior
	std::vector<std::string> right_top = {"Panel derecho superior", "Info 1", "Info 2"};
	std::vector<std::string> right_bottom = {"Panel derecho inferior", "Más info..."};

	// Componente para el panel izquierdo con scroll y ejecución de comandos
	auto left_renderer = Renderer([&] {
		Elements history_lines;
		for (const auto& l : history) {
			history_lines.push_back(text(l));
		}

		auto history_view = vbox(std::move(history_lines)) | vscroll_indicator | frame | flex | focus_end;
		auto prompt_view = hbox({text("$ "), text(input) | inverted});

		return window(text("Panel Izquierdo"),
			vbox({
				history_view,
				separator(),
				prompt_view,
			}));
	});

	// Componente para el panel derecho superior
	auto right_top_renderer = Renderer([&] {
		Elements lines;
		for (const auto& l : right_top) lines.push_back(text(l));
		return window(text("Derecha Arriba"), vbox(std::move(lines)));
	});

	// Componente para el panel derecho inferior
	auto right_bottom_renderer = Renderer([&] {
		Elements lines;
		for (const auto& l : right_bottom) lines.push_back(text(l));
		return window(text("Derecha Abajo"), vbox(std::move(lines)));
	});

	// Layout: panel derecho partido en dos, superior más pequeño
	auto right = Renderer([&] {
		int total_height = screen.dimy();
		int top_height = total_height * 0.3;
		int bottom_height = total_height - top_height;
		return vbox({
			right_top_renderer->Render() | size(HEIGHT, EQUAL, top_height),
			right_bottom_renderer->Render() | size(HEIGHT, EQUAL, bottom_height)
		});
	})->Render();
	// Layout principal: izquierda 70%, derecha 30% (ajustado al ancho del terminal)
	int left_width = 0, right_width = 0;
	auto main_layout = Renderer([&] {
		int total_width = screen.dimx();
		left_width = total_width * 0.7;
		right_width = total_width - left_width;
		return hbox({
			left_renderer->Render() | size(WIDTH, EQUAL, left_width),
			right | size(WIDTH, EQUAL, right_width)
		});
	});

	// Componente raíz para capturar eventos de teclado
	auto main_component = CatchEvent(main_layout, [&](Event event) {
		if (event.is_character()) {
			input += event.character();
			return true;
		}
		if (event == Event::Backspace && !input.empty()) {
			input.pop_back();
			return true;
		}
		if (event == Event::Return) {
			history.push_back("$ " + input);
			// Ejecutar el comando y añadir la salida al historial
			if (!input.empty()) {
				FILE* fp = popen(input.c_str(), "r");
				if (fp) {
					char buf[256];
					while (fgets(buf, sizeof(buf), fp)) {
						std::string line(buf);
						if (!line.empty() && line.back() == '\n') line.pop_back();
						history.push_back(line);
					}
					pclose(fp);
				} else {
					history.push_back("[ERROR] No se pudo ejecutar el comando.");
				}
			}
			input.clear();
			return true;
		}
		// Dejar que otros eventos (ratón, flechas) pasen a los componentes hijos
		return false;
	});

	sscreen.Loop(main_component);
	return 0;
}
