using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace TodoApi.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class TodoController : ControllerBase
    {
        [HttpGet]
        public IActionResult GetTodos()
        {
            var todos = new[]
            {
                new { Id = 1, Title = "Buy groceries", IsCompleted = false },
                new { Id = 2, Title = "Walk the dog", IsCompleted = true },
                new { Id = 3, Title = "Read a book", IsCompleted = false }
            };

            return Ok(todos);
        }
    }
}
