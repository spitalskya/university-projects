package fourier_series;

import java.util.*;

/**
 * Class responsible for all calculations related to complex Fourier series
 */
public class FourierSeriesCalculator {

    /**
     * Returns ordered map from index <code>n</code> to Fourier series coefficient <code>c_n</code>
     * <p>
     *     Each coefficient is calculated by an integral of form
     *     <code>
     *          c_n = ∫_0^1 f(t)*e^(-n2πt)dt
     *      </code>
     * </p>
     *
     * <p>
     *     Results are stored in an ordered map, where indexes are ordered by their absolute value in ascending order.
     *     If two indexes have same absolute value, the positive one comes first.
     * </p>
     *
     *
     * @param functionValues values of the function to calculate Fourier series coefficients from
     * @param numberOfCoefficients how many coefficients should be calculated (minimum 1)
     * @return ordered map from index to Fourier series coefficient for that index
     */
    public static Map<Integer, Complex> calculateFourierCoefficients(
            List<Complex> functionValues, int numberOfCoefficients) {
        Map<Integer, Complex> coefficients = new TreeMap<>(fourierIndexComparator());
        if (numberOfCoefficients < 1) numberOfCoefficients = 1;

        // calculate c_0
        coefficients.put(0, calculateNthFourierCoefficient(functionValues, 0));

        for (int n = 1; n <= (numberOfCoefficients - 1)/ 2; n++){
            // calculate c_n and c_-n
            coefficients.put(n, calculateNthFourierCoefficient(functionValues, n));
            coefficients.put(-n, calculateNthFourierCoefficient(functionValues, -n));
        }

        return coefficients;
    }

    /**
     * Calculates <code>n</code>-th Fourier coefficient
     * <p>
     *     Fourier coefficients are calculated by
     *     <a href="https://math24.net/complex-form-fourier-series.html">formula</a>
     *     <code>
     *         c_n = ∫_0^1 f(t)*e^(-n2πt)dt
     *     </code>
     * </p>
     * <p>
     *     Integral is approximated as a sum of the function values multiplied by length of an integration
     *     interval (1) divided by number of function values. So essentially, it is calculating the
     *     <a href="https://www.khanacademy.org/math/ap-calculus-ab/ab-integration-new/ab-6-2/a/left-and-right-riemann-sums">
     *          left Riemann sum
     *     </a>
     * </p>
     * @param functionValues values of the function to be integrated over the interval [0, 1]
     * @param n index of the Fourier series coefficient
     * @return Fourier series coefficient <code>c_n</code>
     */
    public static Complex calculateNthFourierCoefficient(List<Complex> functionValues, int n) {
        Complex integral = new Complex(0, 0);   // value to store partial integral in

        double t = 0;   // integration variable
        double tIncrement = 1.0 / (functionValues.size());  // length of an interval corresponding to one function value
                                                            // in left Riemann sum

        // left Riemann sum
        for (Complex functionValue : functionValues){
            // add f(t)*e^(-n2πt)*dt to the integral
            integral = integral.add(
                    functionValue.multiply(
                            complexExponential(-n * 2 * Math.PI * t)
                    ).multiply(new Complex(tIncrement, 0))
            );

            t += tIncrement;    // increment the integration variable
        }

        return integral;
    }

    /**
     * Returns result of e^ix as a complex number
     * <p>From Euler's formula: <code>e^ix = cos(x) + i*sin(x)</code></p>
     * @param x argument for the complex exponential
     * @return result of the complex exponential function
     */
    public static Complex complexExponential(double x){
        return new Complex(
                Math.cos(x),
                Math.sin(x)
        );
    }

    /**
     * Returns comparator to be used for ordering Fourier series coefficients
     * <p>
     *     The numbers should be ordered by their absolute value in ascending order.
     *     If absolute values are the same, then the positive number comes first (0, 1, -1, 2, -2,...).
     * </p>
     * @return int comparator
     */
    private static Comparator<Integer> fourierIndexComparator(){
        return (a, b) -> {
            // smaller absolute value first
            int absCompare = Integer.compare(Math.abs(a), Math.abs(b));
            if (absCompare != 0) {
                return absCompare;
            }

            // if absolute values are the same, then positive one first
            return -Integer.compare(a, b);
        };
    }
}
