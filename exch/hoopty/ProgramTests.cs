using NUnit.Framework;
using System.Collections.Generic;

namespace hoopty.Tests
{
    [TestFixture]
    public class ProgramTests
    {
        [Test]
        public void GenerateFillMessage_ShouldReturnCorrectMessage()
        {
            // Arrange
            var fixMessage = new Dictionary<string, string>
            {
                { "8", "FIX.4.2" },
                { "49", "DeutscheBank-800" },
                { "11", "2345" },
                { "54", "1" },
                { "55", "AAPL" },
                { "38", "100" },
                { "44", "150.00" },
                { "40", "2" },
                { "59", "0" },
                { "10", "004" }
            };

            // Act
            string result = Program.GenerateFillMessage(fixMessage);

            // Assert
            Assert.That(result, Does.StartWith("8=FIX.4.2;"));
            Assert.That(result, Does.EndWith("10=004;"));
            Assert.That(result, Does.Contain("17="));
            Assert.That(result, Does.Contain("37="));
            Assert.That(result, Does.Contain("150=2;"));
            Assert.That(result, Does.Contain("14=100;"));
            Assert.That(result, Does.Contain("52="));
            Assert.That(result, Does.Contain("30=HPTY;76=HPTY;"));
        }
    }
}