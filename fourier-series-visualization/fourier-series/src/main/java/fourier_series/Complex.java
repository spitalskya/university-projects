package fourier_series;

/**
 * Class representing a complex number with all basic operations implemented
 */
public class Complex {

    /**
     * Real part of the complex number
     */
    private final double real;

    /**
     * Imaginary part of the complex number
     */
    private final double imag;

    /**
     * Constructs complex number <code>a + bi</code>
     * @param a real part
     * @param b imaginary part
     */
    public Complex(double a, double b){
        real = a;
        imag = b;
    }

    /**
     * Returns real part of the complex number
     * @return real part of the complex number
     */
    public double getReal() {
        return real;
    }

    /**
     * Returns imaginary part of the complex number
     * @return imaginary part of the complex number
     */
    public double getImag() {
        return imag;
    }

    /**
     * Adds <code>other</code> to this complex number
     * @param other complex number to be added
     * @return result of the addition
     */
    public Complex add(Complex other){
        return new Complex(real + other.real, imag + other.imag);
    }

    /**
     * Subtracts <code>other</code> from this complex number
     * @param other complex number to be subtracted
     * @return result of the subtraction
     */
    public Complex subtract(Complex other){
        return new Complex(real - other.real, imag - other.imag);
    }

    /**
     * Multiplies this complex number with <code>other</code>
     * @param other complex number to be multiplied by
     * @return result of the multiplication
     */
    public Complex multiply(Complex other){
        return new Complex(
                real * other.real - imag * other.imag,
                real * other.imag + imag * other.real
        );
    }

    /**
     * Divides this complex number with <code>other</code>
     * @param other complex number to be divided by
     * @return result of the division
     */
    public Complex divide(Complex other){
        if (other.real == 0 && other.imag == 0) throw new ArithmeticException("Dividing by zero: " + other);
        double denom = Math.pow(other.real, 2) + Math.pow(other.imag, 2);
        return new Complex(
                (real * other.real + imag * other.imag)/denom,
                (imag * other.real - real * other.imag)/denom
        );
    }

    /**
     * converts complex number of form <code>a+bi</code> to string
     * @return string of form <code>a+bi</code> or <code>a-bi</code>
     */
    @Override
    public String toString() {
        String sign = (imag>=0)?"+":"";
        return real + sign + imag + "i";
    }
}
