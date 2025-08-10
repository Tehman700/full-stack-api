import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import "./Login.css"; // Import the custom CSS file

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    email: "",
    mobile_number: "",
    role: "viewer", // Set a default role
    first_name: "",
    last_name: "",
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
      const response = await axios.post("http://localhost:8000/api/register/", formData);

      if (response.data.code === 0) {
        setMessage("✅ Registration successful! You can now log in.");
      } else {
        const errors = response.data.errors || {};
        const messages = Object.entries(errors)
          .map(([field, msg]) => `${field}: ${msg}`)
          .join(", ");
        setMessage(`❌ Registration failed: ${messages || response.data.message || "Unknown error"}`);
      }
    } catch (error) {
      setMessage("❌ Registration failed: " + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Framer Motion variants
  const cardVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.8, delay: 0.2 } },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.6 } },
  };

  return (
    <div className="login-page-bg d-flex justify-content-center align-items-center" style={{ minHeight: "100vh" }}>
      <motion.div
        className="card shadow-lg p-4"
        style={{ maxWidth: "600px", width: "100%" }}
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="card-body">
          <h2 className="card-title text-center mb-4 text-primary">Create an Account</h2>
          <p className="text-center text-muted mb-4">Join us and start sharing your thoughts.</p>

          {message && (
            <motion.div
              className={`alert ${message.includes("✅") ? "alert-success" : "alert-danger"}`}
              role="alert"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {message}
            </motion.div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="row">
              <motion.div className="col-md-6 mb-3" variants={itemVariants}>
                <label htmlFor="firstNameInput" className="form-label">First Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="firstNameInput"
                  name="first_name"
                  placeholder="John"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
              </motion.div>
              <motion.div className="col-md-6 mb-3" variants={itemVariants}>
                <label htmlFor="lastNameInput" className="form-label">Last Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="lastNameInput"
                  name="last_name"
                  placeholder="Doe"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
              </motion.div>
            </div>

            <motion.div className="mb-3" variants={itemVariants}>
              <label htmlFor="emailInput" className="form-label">Email Address</label>
              <input
                type="email"
                className="form-control"
                id="emailInput"
                name="email"
                placeholder="name@example.com"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </motion.div>

            <motion.div className="mb-3" variants={itemVariants}>
              <label htmlFor="usernameInput" className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                id="usernameInput"
                name="username"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </motion.div>

            <motion.div className="mb-3" variants={itemVariants}>
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

            <motion.div className="mb-3" variants={itemVariants}>
              <label htmlFor="mobileNumberInput" className="form-label">Mobile Number</label>
              <input
                type="text"
                className="form-control"
                id="mobileNumberInput"
                name="mobile_number"
                placeholder="Mobile Number"
                value={formData.mobile_number}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </motion.div>

            <motion.div className="mb-3" variants={itemVariants}>
                <label htmlFor="roleSelect" className="form-label">Role</label>
                <select
                    className="form-select"
                    id="roleSelect"
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    required
                    disabled={loading}
                >
                    <option value="viewer">Viewer</option>
                    <option value="writer">Writer</option>
                </select>
            </motion.div>

            <div className="d-grid gap-2 mt-4">
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
                    <span className="ms-2">Registering...</span>
                  </>
                ) : (
                  "Register"
                )}
              </motion.button>
            </div>
          </form>

          <p className="text-center mt-3">
            Already have an account? <a href="/login" className="text-decoration-none">Login here</a>
          </p>
        </div>
      </motion.div>
    </div>
  );
}