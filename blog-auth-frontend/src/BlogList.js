import { useEffect, useState } from "react";

function BlogList() {
  const [blogs, setBlogs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Ideally, set your token in localStorage after login, not here
    // But for testing, you can uncomment this once:
    // localStorage.setItem("token", "YOUR_JWT_TOKEN_HERE");

    const token = localStorage.getItem("token");

    if (!token) {
      setError("No token found. Please login first.");
      return;
    }

    fetch("http://localhost:8000/api/blog/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then((data) => setBlogs(data))
      .catch((err) => {
        console.error(err);
        setError(err.message);
      });
  }, []);

  return (
    <div>
      <h1>Blog Posts</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {blogs.length === 0 && !error && <p>No blogs available</p>}
      {blogs.map((blog) => (
        <div key={blog.id}>
          <h2>{blog.title}</h2>
          <p>{blog.content}</p>
        </div>
      ))}
    </div>
  );
}

export default BlogList;
