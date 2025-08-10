import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { motion } from "framer-motion"; // Import motion from framer-motion
import "./Login.css"; // Import the custom CSS file

export default function LoginForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await axios.post("http://localhost:8000/api/login/", formData);

      const isSuccess =
        response.data.code === 0 ||
        response.data.status === 'success' ||
        (response.status === 200 && response.data.data?.tokens?.access);


      if (isSuccess && response.data.data?.tokens?.access) {
        localStorage.setItem("token", response.data.data.tokens.access);
        setMessage("✅ Login Successful! Redirecting...");

        setTimeout(() => {
          navigate("/blogs");
        }, 1000);
      } else {
        // const errors = response.data.errors || {};
        // const messages = Object.entries(errors)
        //   .map(([field, msg]) => `${field}: ${msg}`)
        //   .join(", ");
        setMessage("❌ Login failed: Invalid Credentials");
      }
    } catch (error) {
      setMessage("❌ Login failed: Invalid Credentials");
    } finally {
      setLoading(false);
    }
  };

  // Define Framer Motion variants for animations
  const cardVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, delay: 0.2 } },
  };

  const inputVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.5 } },
  };

  return (
    <div className="login-page-bg d-flex justify-content-center align-items-center" style={{ minHeight: "100vh" }}>
      <motion.div
        className="card shadow-lg p-4 login-card"
        style={{ maxWidth: "400px", width: "100%" }}
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="card-body">
          <h2 className="card-title text-center mb-4 text-primary">Login</h2>

          {message && (
            <motion.div
              className={`alert ${message.includes("✅") ? "alert-success" : "alert-danger"}`}
              role="alert"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {message}
            </motion.div>
          )}

          <form onSubmit={handleSubmit}>
            <motion.div className="mb-3" variants={inputVariants}>
              <label htmlFor="usernameInput" className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                id="usernameInput"
                name="username"
                placeholder="Enter username"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </motion.div>

            <motion.div className="mb-3" variants={inputVariants}>
              <label htmlFor="passwordInput" className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                id="passwordInput"
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </motion.div>

            <div className="d-grid gap-2">
              <motion.button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={loading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                transition={{ duration: 0.2 }}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span className="ms-2">Logging in...</span>
                  </>
                ) : (
                  "Login"
                )}
              </motion.button>
            </div>
          </form>

          <p className="text-center mt-3">
            Don't have an account? <a href="/register" className="text-decoration-none">Register here</a>
          </p>
        </div>
      </motion.div>
    </div>
  );
}