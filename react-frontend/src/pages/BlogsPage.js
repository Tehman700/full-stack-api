import { useState, useEffect } from "react";
import axios from "axios";
import "./Blogs.css";

export default function BlogsPage() {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newComment, setNewComment] = useState({});
  const [newReply, setNewReply] = useState({});
  const [showComments, setShowComments] = useState({});
  const [showReplies, setShowReplies] = useState({});
  const [userRole, setUserRole] = useState(null);
  const [showCreateBlog, setShowCreateBlog] = useState(false);
  const [newBlog, setNewBlog] = useState({ title: "", content: "" });
  const [creatingBlog, setCreatingBlog] = useState(false);

  useEffect(() => {
    fetchUserProfile();
    fetchBlogs();
  }, []);


const fetchUserProfile = async () => {
    try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://localhost:8000/profile_api/profile/", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        // The API returns a 'user' object for a writer
        if (response.data.user && response.data.user.role === 'writer') {
            setUserRole('writer');
        } else {
            // If the 'user' object or role is not 'writer', default to 'viewer'
            setUserRole('viewer');
        }
    } catch (error) {
        console.error("Error fetching user profile:", error);
        // If the API call fails (e.g., a viewer gets a 403 Forbidden), set role to 'viewer'
        setUserRole('viewer');
    }
};

  const fetchBlogs = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get("http://localhost:8000/api/blog/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.data.code === 0) {
        setBlogs(response.data.data || []);
      } else {
        setError(response.data.message || "Failed to fetch blogs");
      }
    } catch (error) {
      console.error("Error fetching blogs:", error);
      setError(error.response?.data?.message || "Failed to fetch blogs");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBlog = async () => {
    if (!newBlog.title.trim() || !newBlog.content.trim()) {
      alert("Please fill in both title and content");
      return;
    }

    setCreatingBlog(true);
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post("http://localhost:8000/api/blog/", {
        title: newBlog.title,
        content: newBlog.content
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.data.code === 0) {
        alert("✅ Blog created successfully! Notifications sent to subscribers.");
        setNewBlog({ title: "", content: "" });
        setShowCreateBlog(false);
        // Refresh blogs to show the new blog
        fetchBlogs();
      } else {
        alert(`❌ Failed to create blog: ${response.data.message}`);
      }
    } catch (error) {
      console.error("Error creating blog:", error);
      alert(`❌ Failed to create blog: ${error.response?.data?.message || error.message}`);
    } finally {
      setCreatingBlog(false);
    }
  };

  const handleBlogReaction = async (blogId, action) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`http://localhost:8000/api/blog/${action}/${blogId}/`, {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Refresh blogs to get updated counts
      fetchBlogs();
    } catch (error) {
      console.error(`Error ${action}ing blog:`, error);
      alert(`Failed to ${action} blog: ${error.response?.data?.message || error.message}`);
    }
  };

  const handleCommentReaction = async (commentId, action) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`http://localhost:8000/api/comment/${action}/${commentId}/`, {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Refresh blogs to get updated counts
      fetchBlogs();
    } catch (error) {
      console.error(`Error ${action}ing comment:`, error);
      alert(`Failed to ${action} comment: ${error.response?.data?.message || error.message}`);
    }
  };

  const handleReplyReaction = async (replyId, action) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`http://localhost:8000/api/reply/${action}/${replyId}/`, {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Refresh blogs to get updated counts
      fetchBlogs();
    } catch (error) {
      console.error(`Error ${action}ing reply:`, error);
      alert(`Failed to ${action} reply: ${error.response?.data?.message || error.message}`);
    }
  };

  const handleSubscribe = async (authorUsername, isSubscribed) => {
    try {
      const token = localStorage.getItem("token");
      const endpoint = isSubscribed ?
        `http://localhost:8000/api/unsubscribe/${authorUsername}/` :
        `http://localhost:8000/api/subscribe/${authorUsername}/`;

      await axios.post(endpoint, {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Refresh blogs to get updated subscription status
      fetchBlogs();
    } catch (error) {
      console.error("Error with subscription:", error);
      alert(`Failed to ${isSubscribed ? 'unsubscribe' : 'subscribe'}: ${error.response?.data?.message || error.message}`);
    }
  };

  const handleAddComment = async (blogId) => {
    const commentText = newComment[blogId];
    if (!commentText?.trim()) return;

    try {
      const token = localStorage.getItem("token");
      await axios.post("http://localhost:8000/api/comment/", {
        blog: blogId,
        comment: commentText
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // Clear the comment input
      setNewComment(prev => ({
        ...prev,
        [blogId]: ""
      }));

      // Refresh blogs to get updated comments
      fetchBlogs();
    } catch (error) {
      console.error("Error adding comment:", error);
      alert(`Failed to add comment: ${error.response?.data?.message || error.message}`);
    }
  };

  const handleAddReply = async (commentId) => {
    const replyText = newReply[commentId];
    if (!replyText?.trim()) return;

    try {
      const token = localStorage.getItem("token");
      await axios.post("http://localhost:8000/api/reply/", {
        comment: commentId,
        reply: replyText
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // Clear the reply input
      setNewReply(prev => ({
        ...prev,
        [commentId]: ""
      }));

      // Refresh blogs to get updated replies
      fetchBlogs();
    } catch (error) {
      console.error("Error adding reply:", error);
      alert(`Failed to add reply: ${error.response?.data?.message || error.message}`);
    }
  };

  const toggleComments = (blogId) => {
    setShowComments(prev => ({
      ...prev,
      [blogId]: !prev[blogId]
    }));
  };

  const toggleReplies = (commentId) => {
    setShowReplies(prev => ({
      ...prev,
      [commentId]: !prev[commentId]
    }));
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "50px" }}>
        <h2>Loading blogs...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: "center", padding: "50px", color: "red" }}>
        <h2>Error: {error}</h2>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "20px" }}>
      {/* Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "30px",
        borderBottom: "2px solid #eee",
        paddingBottom: "15px"
      }}>
        <div>
          <h1 style={{ color: "#333", margin: 0 }}>📝 All Blogs</h1>
          {userRole && (
            <p style={{
              margin: "5px 0 0 0",
              fontSize: "14px",
              color: "#666",
              textTransform: "capitalize"
            }}>
              Role: {userRole}
            </p>
          )}
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          {/* Only show create blog button for writers */}
          {userRole === 'writer' && (
            <button
              onClick={() => setShowCreateBlog(!showCreateBlog)}
              style={{
                padding: "10px 20px",
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "5px"
              }}
            >
              {showCreateBlog ? "❌ Cancel" : "➕ Create Blog"}
            </button>
          )}
          <button
            onClick={handleLogout}
            style={{
              padding: "10px 20px",
              backgroundColor: "#dc3545",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer"
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Create Blog Form - Only show for writers */}
      {userRole === 'writer' && showCreateBlog && (
        <div style={{
          backgroundColor: "#f8f9fa",
          padding: "25px",
          borderRadius: "10px",
          marginBottom: "30px",
          border: "1px solid #dee2e6"
        }}>
          <h3 style={{ color: "#333", marginBottom: "20px" }}>✍️ Create New Blog Post</h3>

          <div style={{ marginBottom: "15px" }}>
            <label style={{
              display: "block",
              marginBottom: "5px",
              fontWeight: "bold",
              color: "#333"
            }}>
              Title:
            </label>
            <input
              type="text"
              value={newBlog.title}
              onChange={(e) => setNewBlog(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Enter your blog title..."
              style={{
                width: "100%",
                padding: "12px",
                border: "1px solid #ddd",
                borderRadius: "6px",
                fontSize: "16px",
                fontFamily: "inherit"
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              marginBottom: "5px",
              fontWeight: "bold",
              color: "#333"
            }}>
              Content:
            </label>
            <textarea
              value={newBlog.content}
              onChange={(e) => setNewBlog(prev => ({ ...prev, content: e.target.value }))}
              placeholder="Write your blog content here..."
              style={{
                width: "100%",
                padding: "12px",
                border: "1px solid #ddd",
                borderRadius: "6px",
                fontSize: "16px",
                minHeight: "200px",
                resize: "vertical",
                fontFamily: "inherit",
                lineHeight: "1.5"
              }}
            />
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={handleCreateBlog}
              disabled={creatingBlog}
              style={{
                padding: "12px 24px",
                backgroundColor: creatingBlog ? "#6c757d" : "#007bff",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: creatingBlog ? "not-allowed" : "pointer",
                fontSize: "16px",
                fontWeight: "bold"
              }}
            >
              {creatingBlog ? "Creating..." : "🚀 Publish Blog"}
            </button>

            <button
              onClick={() => {
                setShowCreateBlog(false);
                setNewBlog({ title: "", content: "" });
              }}
              style={{
                padding: "12px 24px",
                backgroundColor: "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "16px"
              }}
            >
              Cancel
            </button>
          </div>

          <div style={{
            marginTop: "15px",
            padding: "10px",
            backgroundColor: "#d1ecf1",
            borderRadius: "5px",
            fontSize: "14px",
            color: "#0c5460"
          }}>
            📧 <strong>Note:</strong> When you publish this blog, all your subscribers will be automatically notified via email.
          </div>
        </div>
      )}

      {/* Viewer-only message when no create access */}
      {userRole === 'viewer' && (
        <div style={{
          backgroundColor: "#e9ecef",
          padding: "15px",
          borderRadius: "8px",
          marginBottom: "30px",
          textAlign: "center",
          color: "#495057"
        }}>
          📖 You are Browse as a <strong>Viewer</strong>. You can read and interact with blogs, but cannot create new posts.
        </div>
      )}

      {blogs.length === 0 ? (
        <div style={{ textAlign: "center", padding: "50px" }}>
          <h3>No blogs available.</h3>
          {userRole === 'writer' ? (
            <p>Be the first to create a blog post!</p>
          ) : (
            <p>Check back later for new content!</p>
          )}
        </div>
      ) : (
        <div>
          {blogs.map((blog) => (
            <div key={blog.id} style={{
              border: "1px solid #ddd",
              padding: "25px",
              margin: "25px 0",
              borderRadius: "12px",
              boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
              backgroundColor: "white"
            }}>
              {/* Blog Header */}
              <div style={{ marginBottom: "20px" }}>
                <h2 style={{ color: "#333", margin: "0 0 15px 0", fontSize: "24px" }}>{blog.title}</h2>
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  color: "#666",
                  fontSize: "14px",
                  marginBottom: "15px"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
                    <span><strong>By:</strong> {blog.author}</span>
                    <span>👥 {blog.author_subscribers_count} subscribers</span>
                  </div>
                  {blog.is_subscribed !== null && (
                    <button
                      onClick={() => handleSubscribe(blog.author, blog.is_subscribed)}
                      style={{
                        padding: "6px 16px",
                        backgroundColor: blog.is_subscribed ? "#6c757d" : "#007bff",
                        color: "white",
                        border: "none",
                        borderRadius: "20px",
                        fontSize: "12px",
                        cursor: "pointer"
                      }}
                    >
                      {blog.is_subscribed ? "✓ Subscribed" : "+ Subscribe"}
                    </button>
                  )}
                </div>
              </div>

              {/* Blog Content */}
              <div style={{
                marginBottom: "20px",
                lineHeight: "1.7",
                color: "#444",
                fontSize: "16px"
              }}>
                <p>{blog.content}</p>
              </div>

              {/* Blog Reactions */}
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "15px",
                marginBottom: "20px",
                paddingTop: "15px",
                borderTop: "1px solid #eee"
              }}>
                <button
                  onClick={() => handleBlogReaction(blog.id, 'like')}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                    padding: "8px 16px",
                    backgroundColor: "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontSize: "14px"
                  }}
                >
                  👍 Like ({blog.likes})
                </button>

                <button
                  onClick={() => handleBlogReaction(blog.id, 'dislike')}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                    padding: "8px 16px",
                    backgroundColor: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontSize: "14px"
                  }}
                >
                  👎 Dislike ({blog.dislikes})
                </button>

                <button
                  onClick={() => toggleComments(blog.id)}
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#17a2b8",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontSize: "14px"
                  }}
                >
                  💬 Comments ({blog.comments?.length || 0})
                </button>
              </div>

              {/* Comments Section */}
              {showComments[blog.id] && (
                <div style={{
                  backgroundColor: "#f8f9fa",
                  padding: "20px",
                  borderRadius: "8px",
                  marginTop: "15px"
                }}>
                  <h4 style={{ margin: "0 0 15px 0", color: "#333" }}>💬 Comments</h4>

                  {/* Add Comment */}
                  <div style={{ marginBottom: "20px" }}>
                    <textarea
                      value={newComment[blog.id] || ""}
                      onChange={(e) => setNewComment(prev => ({
                        ...prev,
                        [blog.id]: e.target.value
                      }))}
                      placeholder="Write a comment..."
                      style={{
                        width: "100%",
                        padding: "12px",
                        border: "1px solid #ddd",
                        borderRadius: "6px",
                        resize: "vertical",
                        minHeight: "80px",
                        fontFamily: "inherit"
                      }}
                    />
                    <button
                      onClick={() => handleAddComment(blog.id)}
                      style={{
                        marginTop: "10px",
                        padding: "8px 20px",
                        backgroundColor: "#007bff",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        cursor: "pointer"
                      }}
                    >
                      Add Comment
                    </button>
                  </div>

                  {/* Display Comments */}
                  {blog.comments && blog.comments.length > 0 ? (
                    <div>
                      {blog.comments.map((comment) => (
                        <div key={comment.id} style={{
                          backgroundColor: "white",
                          padding: "15px",
                          margin: "15px 0",
                          borderRadius: "8px",
                          border: "1px solid #dee2e6"
                        }}>
                          {/* Comment Header */}
                          <div style={{
                            fontSize: "14px",
                            color: "#666",
                            marginBottom: "8px"
                          }}>
                            <strong>{comment.user || comment.author}</strong>
                            {comment.created && (
                              <span style={{ marginLeft: "10px" }}>
                                {new Date(comment.created).toLocaleDateString()}
                              </span>
                            )}
                          </div>

                          {/* Comment Content */}
                          <p style={{ margin: "0 0 12px 0", color: "#333" }}>
                            {comment.comment}
                          </p>

                          {/* Comment Reactions */}
                          <div style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "10px",
                            marginBottom: "10px"
                          }}>
                            <button
                              onClick={() => handleCommentReaction(comment.id, 'like')}
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "4px",
                                padding: "4px 8px",
                                backgroundColor: "#28a745",
                                color: "white",
                                border: "none",
                                borderRadius: "4px",
                                cursor: "pointer",
                                fontSize: "12px"
                              }}
                            >
                              👍 {comment.likes}
                            </button>

                            <button
                              onClick={() => handleCommentReaction(comment.id, 'dislike')}
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "4px",
                                padding: "4px 8px",
                                backgroundColor: "#dc3545",
                                color: "white",
                                border: "none",
                                borderRadius: "4px",
                                cursor: "pointer",
                                fontSize: "12px"
                              }}
                            >
                              👎 {comment.dislikes}
                            </button>

                            <button
                              onClick={() => toggleReplies(comment.id)}
                              style={{
                                padding: "4px 8px",
                                backgroundColor: "#6c757d",
                                color: "white",
                                border: "none",
                                borderRadius: "4px",
                                cursor: "pointer",
                                fontSize: "12px"
                              }}
                            >
                              🔄 Replies ({comment.replies?.length || 0})
                            </button>
                          </div>

                          {/* Replies Section */}
                          {showReplies[comment.id] && (
                            <div style={{
                              marginLeft: "20px",
                              paddingLeft: "15px",
                              borderLeft: "3px solid #dee2e6"
                            }}>
                              {/* Add Reply */}
                              <div style={{ marginBottom: "15px" }}>
                                <textarea
                                  value={newReply[comment.id] || ""}
                                  onChange={(e) => setNewReply(prev => ({
                                    ...prev,
                                    [comment.id]: e.target.value
                                  }))}
                                  placeholder="Write a reply..."
                                  style={{
                                    width: "100%",
                                    padding: "8px",
                                    border: "1px solid #ddd",
                                    borderRadius: "4px",
                                    resize: "vertical",
                                    minHeight: "60px",
                                    fontSize: "14px"
                                  }}
                                />
                                <button
                                  onClick={() => handleAddReply(comment.id)}
                                  style={{
                                    marginTop: "8px",
                                    padding: "6px 16px",
                                    backgroundColor: "#17a2b8",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                    fontSize: "12px"
                                  }}
                                >
                                  Add Reply
                                </button>
                              </div>

                              {/* Display Replies */}
                              {comment.replies && comment.replies.length > 0 ? (
                                <div>
                                  {comment.replies.map((reply) => (
                                    <div key={reply.id} style={{
                                      backgroundColor: "#f1f3f4",
                                      padding: "12px",
                                      margin: "10px 0",
                                      borderRadius: "6px",
                                      border: "1px solid #e1e5e9"
                                    }}>
                                      <div style={{
                                        fontSize: "12px",
                                        color: "#666",
                                        marginBottom: "6px"
                                      }}>
                                        <strong>{reply.user || reply.author}</strong>
                                        {reply.created && (
                                          <span style={{ marginLeft: "8px" }}>
                                            {new Date(reply.created).toLocaleDateString()}
                                          </span>
                                        )}
                                      </div>
                                      <p style={{ margin: "0 0 8px 0", color: "#333", fontSize: "14px" }}>
                                        {reply.reply}
                                      </p>
                                      <div style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "8px"
                                      }}>
                                        <button
                                          onClick={() => handleReplyReaction(reply.id, 'like')}
                                          style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: "3px",
                                            padding: "3px 6px",
                                            backgroundColor: "#28a745",
                                            color: "white",
                                            border: "none",
                                            borderRadius: "3px",
                                            cursor: "pointer",
                                            fontSize: "11px"
                                          }}
                                        >
                                          👍 {reply.likes}
                                        </button>

                                        <button
                                          onClick={() => handleReplyReaction(reply.id, 'dislike')}
                                          style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: "3px",
                                            padding: "3px 6px",
                                            backgroundColor: "#dc3545",
                                            color: "white",
                                            border: "none",
                                            borderRadius: "3px",
                                            cursor: "pointer",
                                            fontSize: "11px"
                                          }}
                                        >
                                          👎 {reply.dislikes}
                                        </button>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <p style={{ color: "#666", fontStyle: "italic", fontSize: "14px" }}>
                                  No replies yet. Be the first to reply!
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: "#666", fontStyle: "italic" }}>
                      No comments yet. Be the first to comment!
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}