/**
 * Provides classes for approximating drawn curves by Fourier series using JavaFX.
 *
 * <p>This module requires the following:
 * <ul>
 *   <li><code>javafx.controls</code></li>
 *   <li><code>javafx.fxml</code></li>
 * </ul>
 *
 * <p>The following packages are exported:
 * <ul>
 *   <li><code>fourier_series</code> - contains the main application classes for Fourier series visualization.</li>
 * </ul>
 */
module fourier_series {
    requires javafx.controls;
    requires javafx.fxml;


    opens fourier_series to javafx.fxml;
    exports fourier_series;
}