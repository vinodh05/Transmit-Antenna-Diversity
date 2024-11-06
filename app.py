from flask import Flask, render_template, send_file, jsonify,request
from multiprocessing import Process
import os
from manim import *

app = Flask(__name__)

# Global flag to check if video generation is complete
is_generating = False
output_path = "static/videos/videos/1080p60/antenna_animation.mp4"

from manim import *
import numpy as np

class MultipleAntennaTransmission(Scene):

    def __init__(self, antennaSlider, **kwargs):
        super().__init__(**kwargs)
        self.antennaSlider = int(antennaSlider)
    
    def construct(self):
        # n = 4  # Number of transmit antennas
        n = self.antennaSlider
        sigma = 0.5  # Standard deviation for noise
        
        # Create fixed layout positions
        # Main area will be from x=-6 to x=2
        # Calculation area will be from x=2 to x=6
        main_area_center = -2  # Center point for main transmission area
        calc_area_center = 4   # Center point for calculation area

        # Assumptions at the top
        # Assumptions at the top right corner, with each equation on a new line
        assumptions = VGroup(
            MathTex(r"h \sim \mathcal{CN}(0,1)", color=WHITE).scale(0.55),
            MathTex(r"w \sim \mathcal{CN}(0, \sigma^2)", color=WHITE).scale(0.55)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(UR).shift(LEFT*0.5)

        self.play(Write(assumptions))


        # Transmitter and receiver labels
        transmitter_label = Text("Transmitter", color=BLUE, slant=ITALIC).scale(0.6)
        transmitter_label.move_to([-5.5, -2, 0])  # Left side of main area
        receiver_label = Text("Receiver", color=GREEN, slant=ITALIC).scale(0.6)
        receiver_label.move_to([1.5, -2, 0])      # Right side of main area

        # Transmit antennas
        tx_antennas = VGroup(*[
            VGroup(
                Line(LEFT * 0.8, LEFT * 0.4, color=BLUE),
                Line(LEFT * 0.4, LEFT * 0.4 + UP * 0.6, color=BLUE),
                Polygon(LEFT * 0.4 + UP * 0.6, LEFT * 0.4 + UP * 0.9 + RIGHT * 0.2, LEFT * 0.4 + UP * 0.9 + LEFT * 0.2, color=BLUE)
            ).shift(DOWN * i * 1.1)
            for i in range(n)
        ]).next_to(transmitter_label, UP, buff=0.5)

        # Receiver antenna
        rx_antenna = VGroup(
            Line(RIGHT * 0.8, RIGHT * 0.4, color=GREEN),
            Line(RIGHT * 0.4, RIGHT * 0.4 + UP * 0.6, color=GREEN),
            Polygon(RIGHT * 0.4 + UP * 0.6, RIGHT * 0.4 + UP * 0.9 + LEFT * 0.2, RIGHT * 0.4 + UP * 0.9 + RIGHT * 0.2, color=GREEN)
        ).next_to(receiver_label, UP, buff=0.3).shift(UP*0.5)

        self.play(Write(transmitter_label), Write(receiver_label), Create(tx_antennas), Create(rx_antenna))

        # Initialize calculation display area
        # Position 'Channel Parameters' below 'Assumptions'
        calc_title = Text("Channel Parameters", color=YELLOW).scale(0.5)
        calc_title.next_to(assumptions, DOWN, buff=0.5)  # Position below 'assumptions' with buffer space
        calc_title.to_edge(RIGHT, buff=0.5).shift(LEFT*0.5)  # Align it towards the right edge with some buffer
        self.play(Write(calc_title))


        symbols = [-1]
        
        for symbol_index, bpsk_symbol in enumerate(symbols):
            # Clear previous calculations
            if symbol_index > 0:
                self.play(*[FadeOut(mob) for mob in self.mobjects if mob not in [assumptions, transmitter_label, receiver_label, tx_antennas, rx_antenna, calc_title]])

            h_vector = VGroup()
            w_vector = VGroup()
            y_vector = VGroup()
            y_values = []
            

            # Create vector headers in calculation area
            h_header = MathTex(r"\mathbf{h} = ").scale(0.5).next_to(calc_title, DOWN, buff=0.2).shift(LEFT * 1.8)
            w_header = MathTex(r"\mathbf{w} = ").scale(0.5).next_to(h_header, RIGHT, buff=0.2).shift(RIGHT * 1.1)
            y_header = MathTex(r"\mathbf{y} = ").scale(0.5).next_to(w_header, RIGHT, buff=0.2).shift(RIGHT * 1.1)

            self.play(Write(h_header), Write(w_header), Write(y_header))

            # Loop through each antenna
            for i, tx_antenna in enumerate(tx_antennas):
                # Generate random h and w
                h = np.random.normal(0, 1) + 1j * np.random.normal(0, 1)
                w = np.random.normal(0, sigma) + 1j * np.random.normal(0, sigma)
                y_i = h * bpsk_symbol + w
                y_values.append(y_i)
                

                # Dim other antennas
                self.play(*[antenna.animate.set_opacity(0.2) for antenna in tx_antennas if antenna != tx_antenna])
                
                # Show symbol being transmitted
                symbol_label = MathTex(f"x = {bpsk_symbol}", color=WHITE).scale(0.8).next_to(tx_antenna, LEFT, buff=0.3)
                self.play(Write(symbol_label), tx_antenna.animate.set_color(YELLOW))

                # Show transmission
                wave_arrow = Arrow(start=tx_antenna.get_right(), end=rx_antenna.get_left(), color=YELLOW, buff=0.1)
                self.play(Create(wave_arrow))

                # Update vectors in calculation area
                h_entry = MathTex(f"{h:.2f}", color=YELLOW).scale(0.5)
                w_entry = MathTex(f"{w:.2f}", color=RED).scale(0.5)
                y_entry = MathTex(f"{y_i:.2f}", color=WHITE).scale(0.5)

                if i == 0:
                    h_entry.next_to(h_header, DOWN, buff=0.2)
                    w_entry.next_to(w_header, DOWN, buff=0.2)
                    y_entry.next_to(y_header, DOWN, buff=0.2)
                else:
                    h_entry.next_to(h_vector[-1], DOWN, buff=0.2)
                    w_entry.next_to(w_vector[-1], DOWN, buff=0.2)
                    y_entry.next_to(y_vector[-1], DOWN, buff=0.2)

                h_vector.add(h_entry)
                w_vector.add(w_entry)
                y_vector.add(y_entry)

                self.play(Write(h_entry), Write(w_entry), Write(y_entry))

                # Clean up transmission animation
                self.play(FadeOut(wave_arrow), tx_antenna.animate.set_color(BLUE))
                self.play(*[antenna.animate.set_opacity(1.0) for antenna in tx_antennas])

            # # Add matrix brackets
            # h_brace = Brace(h_vector, LEFT)
            # w_brace = Brace(w_vector, LEFT)
            # y_brace = Brace(y_vector, LEFT)
            # self.play(Create(h_brace), Create(w_brace), Create(y_brace))

            # Calculate and display ML metric
            # Conjugate and compute ML metric
            h_conj = np.conjugate(y_values)
            ml_metric = np.real(np.dot(h_conj, y_values))

            # Arrange ML Metric and value on the same line
            ml_calculation = VGroup(
                MathTex(r"\text{ML Metric} = \text{Re}\left\{\mathbf{h}^H\mathbf{y}\right\} =", color=YELLOW).scale(0.6),
                MathTex(f"{ml_metric:.2f}", color=WHITE).scale(0.6)
            ).arrange(RIGHT, buff=0.2).shift(RIGHT*1.5)  # Place components side-by-side with some buffer

            # Move ML calculation towards the right and lower the position
            calc_area_center = 4.8  # or any desired position to the right
            ml_calculation.move_to([calc_area_center, -1, 0])

            # Compute decoded symbol and position the label below
            decoded_symbol = 1 if ml_metric > 0 else -1
            final_decoded_label = MathTex(
                f"\\text{{ML Decoded Symbol: }} x = {decoded_symbol}",
                color=WHITE
            ).scale(0.6).next_to(ml_calculation, DOWN, buff=0.3)  # Position directly below with slight buffer

            # Display ML calculation and decoded symbol
            self.play(Write(ml_calculation), Write(final_decoded_label))


            # Fade out calculations before next symbol iteration
            self.play(FadeOut(ml_calculation), FadeOut(final_decoded_label))
            
    def create_wave_arrow(self, start, end):
        """Create a single arrow representing the signal wave."""
        wave_arrow = Arrow(start=start, end=end, color=YELLOW, buff=0.1)
        return wave_arrow


def generate_animation(antennaSlider):
    global is_generating
    is_generating = True

    # Ensure the output directory exists
    os.makedirs("static/videos", exist_ok=True)

    # Run Manim to generate the video
    config.media_dir = "static/videos/"  # Set output directory
    config.output_file = "antenna_animation.mp4"  # Define output file
    scene = MultipleAntennaTransmission(antennaSlider)
    scene.render()  # This will save to the specified path

    is_generating = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_video", methods=["POST"])
def generate_video():
    antennaSlider = request.form.get('antennaSlider')
    print("hello",antennaSlider)
    if antennaSlider is None:
        return jsonify({"error": "antennaSlider is required"}), 400
    # Start the animation generation in a background process
    p = Process(target=generate_animation,args=(antennaSlider,))
    p.start()
    return jsonify({"status": "started"})


@app.route("/check_status")
def check_status():
    global is_generating
    if is_generating:
        return jsonify({"status": "generating"})
    elif os.path.exists(output_path):
        return jsonify({"status": "ready"})
    else:
        return jsonify({"status": "error"})


@app.route("/get_video")
def get_video():
    return send_file(output_path, as_attachment=False)


if __name__ == "__main__":
    app.run(host="10.23.13.108", port=5003, debug=True)