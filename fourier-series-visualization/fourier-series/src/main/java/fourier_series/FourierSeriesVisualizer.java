package fourier_series;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.Slider;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.shape.Polyline;
import javafx.stage.Stage;
import javafx.scene.control.Button;
import javafx.util.Duration;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * Class responsible for displaying complex Fourier series of a drawn shape
 */
public class FourierSeriesVisualizer extends Application {

    /**
     * root pane of the graphic application
     */
    private final BorderPane root = new BorderPane();

    /**
     * label displaying current status of the visualization or some action needed
     */
    private final Label labelStatus = new Label("Fourier series visualizer");

    /**
     * button to start drawing process
     */
    private final Button buttonDraw = new Button("Draw");

    /**
     * button to showcase drawing PI with Fourier series
     */
    private final Button buttonDrawPI = new Button("Draw PI");

    /**
     * button that turns on/off displaying circles around Fourier series vectors
     */
    private final Button buttonDrawCircles = new Button("Show circles");

    /**
     * slider which determines order (10^sliderValue) of how many points will be used from the drawn shape
     * to calculate Fourier series coefficients
     */
    private final Slider sliderSamplingFrequency = new Slider();

    /**
     * label displaying title and the value of <code>sliderSamplingFrequency</code>
     */
    private final Label labelSamplingFrequency = new Label();

    /**
     * slider which determines the number of coefficients used in Fourier series
     */
    private final Slider sliderNumberOfCoefficients = new Slider();

    /**
     * label displaying title and the value of <code>sliderNumberOfCoefficients</code>
     */private final Label labelNumberOfCoefficients = new Label();

    /**
     * method to start Fourier series visualization application
     * @param primaryStage stage for the application
     */
    @Override
    public void start(Stage primaryStage) {
        // configure top panel
        labelStatus.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        HBox topPanel = new HBox(labelStatus);
        topPanel.setAlignment(Pos.CENTER);
        topPanel.setSpacing(40);
        topPanel.setStyle("-fx-background-color: #C2C2C2;");
        root.setTop(topPanel);

        // configure bottom panel
        // create sliders and align them vertically with their labels
        configureSliders();
        VBox numberOfCoefficients = new VBox(5, labelNumberOfCoefficients, sliderNumberOfCoefficients);
        VBox samplingFrequency = new VBox(5, labelSamplingFrequency, sliderSamplingFrequency);

        // group relevant pieces in HBox
        HBox bottomPanel = new HBox(buttonDraw, buttonDrawPI, buttonDrawCircles,
                numberOfCoefficients, samplingFrequency);
        bottomPanel.setAlignment(Pos.CENTER);
        bottomPanel.setSpacing(20);
        bottomPanel.setStyle("-fx-background-color: #C2C2C2;");
        root.setBottom(bottomPanel);

        // create DrawPane in the center
        root.setCenter(new DrawPane());

        // show the app
        primaryStage.setTitle("Fourier Series Visualizer");
        primaryStage.setScene(new Scene(root));
        primaryStage.show();
    }

    /**
     * main method that launches the Fourier series visualizer app
     * @param args command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }

    /**
     * configures sliders used in the application
     * <p>
     *     Sets their min/max value, initial value and binds their value with String displayed in corresponding label
     * </p>
     */
    private void configureSliders(){
        sliderSamplingFrequency.setMin(2);
        sliderSamplingFrequency.setMax(6);
        sliderSamplingFrequency.setValue(3);
        sliderSamplingFrequency.setShowTickLabels(true);
        sliderSamplingFrequency.setMajorTickUnit(1);
        labelSamplingFrequency.setText(String.format("Order of precision %.0f", sliderSamplingFrequency.getValue()));
        sliderSamplingFrequency.valueProperty().addListener((obs, oldVal, newVal) -> {
            labelSamplingFrequency.setText(String.format("Order of precision %d", newVal.intValue()));
        });

        sliderNumberOfCoefficients.setMin(1);
        sliderNumberOfCoefficients.setMax(201);
        sliderNumberOfCoefficients.setValue(101);
        sliderNumberOfCoefficients.setShowTickLabels(true);
        sliderNumberOfCoefficients.setMajorTickUnit(50);
        labelNumberOfCoefficients.setText(String.format("Number of Fourier coefficients %.0f",
                sliderNumberOfCoefficients.getValue()));
        sliderNumberOfCoefficients.valueProperty().addListener((obs, oldVal, newVal) -> {
            labelNumberOfCoefficients.setText(String.format("Number of Fourier coefficients %d", newVal.intValue()));
        });

        // number of coefficients needs to be odd
        sliderNumberOfCoefficients.valueProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal.intValue() % 2 == 0){
                sliderNumberOfCoefficients.setValue(newVal.intValue() - 1);
            }
            labelNumberOfCoefficients.setText(String.format("Number of Fourier coefficients %d", newVal.intValue() - 1));
        });
    }

    /**
     * center part of the application, responsible for interacting with the user and plotting the Fourier series
     */
    class DrawPane extends Pane{

        // Constants
        /**
         * milliseconds between frames of Fourier series visualization animation
         */
        public final int TIMELINE_FRAME_DURATION_MILLIS = 10;

        /**
         * increment of time in each frame in Fourier series visualization
         */
        public final double FOURIER_FRAME_TIME_INCREMENT = 0.001;

        /**
         * how long is the curve drawn by Fourier series in proportion to drawn curve
         */
        public final double FACTOR_OF_PATH_LENGTH_TO_DRAW = 0.9;

        /**
         * maximum number of Fourier coefficients
         */
        public final int MAXIMUM_NUMBER_OF_FOURIER_COEFFICIENTS = 201;

        // Drawing phase
        /**
         * whether drawing by user is expected
         */
        private boolean drawing = false;

        /**
         * first point of the drawn path by user
         */
        private Double[] firstPoint = null;

        /**
         * last point of the drawn path by user
         */
        private Double[] lastPoint = null;

        /**
         * list of all points that were drawn by the user
         */
        private List<Double[]> path = new ArrayList<>();

        // Fourier related
        /**
         * map from index to Fourier coefficient for drawn path
         */
        private Map<Integer, Complex> fourierCoefficients = null;

        /**
         * time variable for Fourier series plotting
         */
        private double time = 0;

        /**
         * Timeline responsible for updating the Fourier series animation
         */
        private Timeline timer = null;

        /**
         * list of plotted points by Fourier series
         */
        private final List<Double[]> plottedPath = new ArrayList<>();

        /**
         * whether to draw circles around Fourier series vectors
         */
        private boolean drawCircles = true;

        // PI
        /**
         * name of the file where serialized list of points (<code>Double[]</code>) for drawing PI is stored
         */
        String serializedPIFileName = "pi.ser";

        /**
         * sets all necessary interactions of user and application
         * <p>App is either in the: </p>
         * <ul>
         *      <li>drawing phase - expects user to draw a curve in the window</li>
         *      <li>Fourier phase - the approximation of the drawn curve is drawn by the Fourier series</li>
         * </ul>
         */
        public DrawPane(){
            setPrefSize(800, 800);

            // if mouse is dragged during the drawing phase, draw the path
            setOnMouseDragged(event -> {
                if (!drawing) return;

                double x = event.getX();
                double y = event.getY();

                // store the first point if it wasn't stored before
                if (firstPoint == null){
                    firstPoint = new Double[]{x, y};
                }

                // if only one point was drawn, store it and don't continue
                if (lastPoint == null){
                    lastPoint = new Double[]{x, y};
                    path.add(Arrays.copyOf(lastPoint, 2));
                    return;
                }

                // if there is more than one point drawn, draw a line between last drawn point and current
                // mouse coordinates, then store them in the `path`
                Line l = new Line(lastPoint[0], lastPoint[1], x, y);
                l.setStrokeWidth(2);
                getChildren().add(l);

                lastPoint = new Double[]{x, y};
                path.add(Arrays.copyOf(lastPoint, 2));
            });

            // when mouse is released from the drag in the drawing path, enclose the drawing to form a closed curve
            // and stared computing and drawing Fourier series
            setOnMouseReleased(event -> {
                if (!drawing) return;
                // enclose the curve
                if (firstPoint == null || lastPoint == null) return;
                Line l = new Line(lastPoint[0], lastPoint[1], firstPoint[0], firstPoint[1]);
                getChildren().add(l);

                // drawing phase ended
                drawing = false;

                fourierPhase();
            });

            // button should start the drawing phase
            buttonDraw.setOnAction(event -> {
                drawPhase();
            });

            // button that sets whether the circles around Fourier series vectors should be displayed
            buttonDrawCircles.setOnAction(event -> {
                drawCircles = !drawCircles;
                buttonDrawCircles.setText((drawCircles)?"Don't show circles":"Show circles");
            });

            // button that simulates drawing PI by user and approximates it by Fourier series
            // FIXME takes a few seconds
            buttonDrawPI.setOnAction(event -> {
                drawPi();
            });

            // on change of this slider, if in Fourier phase, recalculate the coefficients and start drawing again
            sliderNumberOfCoefficients.valueProperty().addListener((obs, oldVal, newVal) -> {
                if(!drawing) fourierPhase();
            });

            // change the maximum number for the slider for number of coefficients based on the field
            sliderNumberOfCoefficients.setMax(MAXIMUM_NUMBER_OF_FOURIER_COEFFICIENTS);

            // on change of this slider, if in Fourier phase, recalculate the coefficients and start drawing again
            sliderSamplingFrequency.valueProperty().addListener((obs, oldVal, newVal) -> {
                if(!drawing) fourierPhase();
            });

            // start by drawing PI
            drawPi();
        }

        /**
         * method that simulates drawing PI by the user and then Fourier approximation is displayed
         * <b>takes a few seconds</b>
         */
        private void drawPi(){
            resetBeforeDraw();
            drawing = false;
            labelStatus.setText("Loading PI path");

            // load PI path from the serialized list
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(serializedPIFileName))) {
                path = (List<Double[]>) ois.readObject();
            } catch (IOException | ClassNotFoundException e) {
                e.printStackTrace();
            }

            // calculate and draw the Fourier series for this PI path
            fourierPhase();
        }

        /**
         * updates the label for the draw phase and resets all the necessary fields
         */
        private void drawPhase(){
            labelStatus.setText("Draw an enclosed curve");
            resetBeforeDraw();
        }

        /**
         * resets all the necessary fields for the draw phase
         */
        private void resetBeforeDraw(){
            // clear all the drawn shapes
            getChildren().clear();

            // clear fields for drawn path
            firstPoint = null;
            lastPoint = null;
            path.clear();

            // clear fourier related stuff (so that the timeline is stopped)
            resetBeforeFourierDraw();

            // start the drawing phase
            drawing = true;
        }

        /**
         * controls the flow of Fourier phase
         * <p>Clears all the necessary fields, calculates the coefficients, draws the Fourier series</p>
         */
        private void fourierPhase(){
            resetBeforeFourierDraw();
            labelStatus.setText("Calculating Fourier coefficients");
            calculateFourierCoefficients();
            labelStatus.setText("Drawing complex Fourier series");
            drawFourier();
        }

        /**
         * resets fields necessary for Fourier phase
         * <p>That is plotted path by the Fourier series before, time variable and timer Timeline </p>
         */
        private void resetBeforeFourierDraw(){
            plottedPath.clear();

            time = 0;
            if (timer != null){
                timer.stop();
                timer = null;
            }
        }

        /**
         * calculates Fourier coefficients for drawn curve
         * <p>
         *     The curve - list of 2D points is looked at as a values of a function from [0, 1] to complex numbers.
         *     We take 10^(value of <code>sliderSamplingFrequency</code>) equally distanced
         *     (by index) points from this curve.
         * </p>
         * <p>
         *     These "function values" are passed to
         *     <code>FourierSeriesCalculator.calculateFourierCoefficients()</code>, which returns Fourier coefficients.
         *     When we use these in Fourier series, we get an approximation of the drawn shape by the user.
         * </p>
         */
        private void calculateFourierCoefficients(){
            // determine number of points (function values) to pass to `FourierSeriesCalculator`
            int numberOfPoints = (int) Math.pow(10, sliderSamplingFrequency.getValue());

            // extract `numberOfPoints` points from `path` so that they are equally distanced from each-other by index
            // additionally, convert those points to complex numbers
            List<Complex> strippedPath = new ArrayList<>();
            if (path.size() < numberOfPoints){      // if size of the path is less than `numberOfPoints`, don't strip
                path.forEach(point -> strippedPath.add(new Complex(point[0], point[1])));
            } else {
                double step = (double) (path.size()) / (numberOfPoints - 1);

                for (int i = 0; i < numberOfPoints; i++) {
                    int index = (int) (i * step);
                    if (index >= path.size()) break;
                    Double[] ithPoint = path.get(index);
                    strippedPath.add(new Complex(ithPoint[0], ithPoint[1]));
                }
            }

            // calculate Fourier coefficients
            fourierCoefficients = FourierSeriesCalculator.calculateFourierCoefficients(
                    strippedPath, (int) sliderNumberOfCoefficients.getValue()
                );
        }

        /**
         * draws complex Fourier series approximating the drawn shape
         * <p>
         *     Takes calculated fourier coefficients and displays a complex number: <br>
         *     <code>c_0*e^(i*0*2πt) + c_1*e^(i*1*2πt) + c_-1*e^(i*-1*2πt) + ...</code> <br>
         *     Each term of the sum is displayed as a vector in complex plane
         * </p>
         */
        private void drawFourier(){
            if (fourierCoefficients == null) return;
            // set up a Timeline that updates the animation of Fourier series
            timer = new Timeline(new KeyFrame(Duration.millis(TIMELINE_FRAME_DURATION_MILLIS), e -> {
                // increment time variable
                time += FOURIER_FRAME_TIME_INCREMENT;

                getChildren().clear();

                // draw drawn shape by user
                drawDrawnShape();
                // draw Fourier series as vectors in complex plane
                drawFourierVectors();
                // draw path "traveled" by the Fourier series
                drawPlottedShape();
            }));

            timer.setCycleCount(Timeline.INDEFINITE);
            timer.play();
        }

        /**
         * in Fourier phase, re-draws shape drawn by the user
         */
        private void drawDrawnShape(){
            Polyline drawnShape = new Polyline();
            for (Double[] point : path) {
                drawnShape.getPoints().addAll(point[0], point[1]);
            }
            drawnShape.getPoints().addAll(path.get(0)[0], path.get(0)[1]);
            drawnShape.setStroke(Color.GRAY);
            drawnShape.setStrokeWidth(2);
            getChildren().add(drawnShape);
        }

        /**
         * draws Fourier series where <code>t=time</code> as a sum of vectors in complex plane
         */
        private void drawFourierVectors(){
            Polyline fourierVectors = new Polyline(0, 0);

            // partial sum of complex number
            Double[] sumOfVectors = new Double[] {0.0, 0.0};

            fourierCoefficients.forEach((index, coeff) -> {
                // caculate c_n*e^(in2πt) and convert the complex number to a point in the complex plane
                Double[] nextPoint = complexToDoubleArray(
                        coeff.multiply(
                                FourierSeriesCalculator.complexExponential(index * 2 * Math.PI * time)
                        )
                );

                // add the point to the polyline
                nextPoint[0] += sumOfVectors[0];
                nextPoint[1] += sumOfVectors[1];
                fourierVectors.getPoints().addAll(nextPoint[0], nextPoint[1]);

                // if circles should be drawn, pass its center and a point to calculate the radius
                if (drawCircles) {
                    drawCircle(sumOfVectors[0], sumOfVectors[1], nextPoint[0], nextPoint[1]);
                }

                // update the partial sum
                sumOfVectors[0] = nextPoint[0];
                sumOfVectors[1] = nextPoint[1];
            });

            // add Fourier series to the pane
            fourierVectors.setStroke(Color.DARKGRAY);
            getChildren().add(fourierVectors);

            // add resulting point in the complex pane to the list of points that represent path "traveled"
            // by the Fourier series to be plotted
            // if the length of this list is too big (determined by the factor, shorten it)
            if (plottedPath.size() >= (int) (FACTOR_OF_PATH_LENGTH_TO_DRAW * (1/FOURIER_FRAME_TIME_INCREMENT))){
                plottedPath.remove(0);
            }
            plottedPath.add(Arrays.copyOf(sumOfVectors, 2));
        }

        /**
         * draws circle defined by the passed coordinates
         * @param x1 x coordinate of the center
         * @param y1 y coordinate of the center
         * @param x2 x coordinate of a point on the circumference
         * @param y2 y coordinate of a point on the circumference
         */
        private void drawCircle(double x1, double y1, double x2, double y2){
            double radius = Math.sqrt(
                    Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2)
                );
            Circle c = new Circle(x1, y1, radius);
            c.setStroke(Color.DARKGRAY);
            c.setFill(Color.TRANSPARENT);
            getChildren().add(c);
        }

        /**
         * draws path already "traveled" by the Fourier series
         */
        public void drawPlottedShape(){
            Polyline plottedShape = new Polyline();
            for (Double[] plottedPoint : plottedPath) {
                plottedShape.getPoints().addAll(plottedPoint[0], plottedPoint[1]);
            }
            plottedShape.setStroke(Color.BLUEVIOLET);
            plottedShape.setStrokeWidth(2);
            getChildren().add(plottedShape);
        }

        /**
         * converts complex number to a double array
         * @param c complex number of form <code>a+bi</code>
         * @return double array <code>[a, b]</code>
         */
        private Double[] complexToDoubleArray(Complex c){
            return new Double[]{c.getReal(), c.getImag()};
        }
    }
}
